"""
Advanced IPC Section Parser with LLM-based extraction
Uses LangChain and OpenAI to intelligently extract and structure IPC sections
"""

import re
import json
from pathlib import Path
from typing import List, Dict, Optional
import PyPDF2
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# Load environment variables
load_dotenv()
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field


class IPCSection(BaseModel):
    """Structured model for IPC section"""
    jurisdiction: str = Field(default="India", description="Jurisdiction of the law")
    law: str = Field(default="IPC", description="Name of the law (e.g., IPC)")
    section: str = Field(description="Section number (e.g., '420', '302')")
    title: str = Field(description="Title or heading of the section")
    text: str = Field(description="Complete text of the section")
    chapter: Optional[str] = Field(default=None, description="Chapter if available")
    punishment: Optional[str] = Field(default=None, description="Punishment details if mentioned")


class AdvancedIPCExtractor:
    """Advanced IPC extractor using LLM for better accuracy"""
    
    def __init__(self, pdf_path: str, use_llm: bool = False):
        self.pdf_path = pdf_path
        self.use_llm = use_llm
        
        if use_llm:
            self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
            self.parser = PydanticOutputParser(pydantic_object=IPCSection)
    
    def extract_text_from_pdf(self) -> str:
        """Extract raw text from PDF"""
        print(f"📖 Extracting text from {self.pdf_path}...")
        
        text = ""
        try:
            with open(self.pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                total_pages = len(pdf_reader.pages)
                print(f"Total pages: {total_pages}")
                
                for page_num, page in enumerate(pdf_reader.pages, 1):
                    if page_num % 10 == 0:
                        print(f"Processing page {page_num}/{total_pages}...")
                    page_text = page.extract_text()
                    text += page_text + "\n"
                    
        except Exception as e:
            print(f"❌ Error extracting PDF: {e}")
            raise
            
        print(f"✅ Extracted {len(text)} characters from {total_pages} pages")
        return text
    
    def chunk_text_by_section(self, text: str) -> List[str]:
        """Split text into chunks by section markers"""
        print("\n🔪 Chunking text by sections...")
        
        # Split by common section patterns
        # Matches patterns like: "Section 420", "420.", etc.
        chunks = re.split(r'\n(?=\d+[A-Z]?\.|\bSection\s+\d+[A-Z]?\b)', text)
        
        # Filter empty chunks
        chunks = [chunk.strip() for chunk in chunks if chunk.strip() and len(chunk.strip()) > 20]
        
        print(f"✅ Created {len(chunks)} chunks")
        return chunks
    
    def parse_section_regex(self, chunk: str) -> Optional[Dict]:
        """Parse section using regex patterns"""
        
        # Try multiple patterns
        patterns = [
            # Pattern 1: "Section 420. Title.—Text"
            r'^(?:Section\s+)?(\d+[A-Z]?)\.\s*([^.—\-–]+?)\.?\s*[—\-–]\s*(.*)',
            # Pattern 2: "420. Title—Text"
            r'^(\d+[A-Z]?)\.\s*([^.—\-–]+?)\s*[—\-–]\s*(.*)',
            # Pattern 3: "Section 420: Title - Text"
            r'^(?:Section\s+)?(\d+[A-Z]?)[:\.]\s*([^:—\-–]+?)\s*[:\-–—]\s*(.*)',
        ]
        
        for pattern in patterns:
            match = re.match(pattern, chunk.strip(), re.DOTALL | re.IGNORECASE)
            if match:
                section_num = match.group(1).strip()
                title = match.group(2).strip()
                text = match.group(3).strip()
                
                # Clean up text
                text = re.sub(r'\s+', ' ', text)
                title = re.sub(r'\s+', ' ', title)
                
                # Extract punishment if mentioned
                punishment = None
                punishment_match = re.search(
                    r'(?:shall be punished|punishment|imprisonment|fine).*?(?:\.|$)',
                    text,
                    re.IGNORECASE
                )
                if punishment_match:
                    punishment = punishment_match.group(0)
                
                return {
                    "jurisdiction": "India",
                    "law": "IPC",
                    "section": section_num,
                    "title": title,
                    "text": text,
                    "punishment": punishment
                }
        
        return None
    
    def parse_section_llm(self, chunk: str) -> Optional[Dict]:
        """Parse section using LLM for better accuracy"""
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert at extracting structured information from Indian legal documents.
Extract the section number, title, and complete text from the given IPC section.

{format_instructions}

Only extract if this appears to be a valid IPC section. If not, return null."""),
            ("human", "{text}")
        ])
        
        try:
            messages = prompt.format_messages(
                text=chunk[:2000],  # Limit to avoid token issues
                format_instructions=self.parser.get_format_instructions()
            )
            
            response = self.llm.invoke(messages)
            parsed = self.parser.parse(response.content)
            
            return parsed.dict()
            
        except Exception as e:
            print(f"⚠️  LLM parsing failed for chunk: {str(e)[:100]}")
            return None
    
    def extract_sections(self, text: str) -> List[Dict]:
        """Extract all sections from text"""
        print("\n🔍 Extracting IPC sections...")
        
        chunks = self.chunk_text_by_section(text)
        sections = []
        
        for i, chunk in enumerate(chunks, 1):
            if i % 50 == 0:
                print(f"Processing chunk {i}/{len(chunks)}...")
            
            # Try regex first (faster)
            section = self.parse_section_regex(chunk)
            
            # If regex fails and LLM is enabled, try LLM
            if not section and self.use_llm:
                section = self.parse_section_llm(chunk)
            
            if section:
                sections.append(section)
        
        print(f"✅ Extracted {len(sections)} valid sections")
        return sections
    
    def save_to_json(self, sections: List[Dict], output_path: str):
        """Save sections to JSON file"""
        print(f"\n💾 Saving to {output_path}...")
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(sections, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Saved {len(sections)} sections")
    
    def run(self, output_path: str) -> List[Dict]:
        """Run complete extraction pipeline"""
        print("🚀 Starting advanced IPC extraction...\n")
        
        # Extract text
        text = self.extract_text_from_pdf()
        
        # Extract sections
        sections = self.extract_sections(text)
        
        # Save results
        if sections:
            self.save_to_json(sections, output_path)
            
            # Print statistics
            print("\n📊 Extraction Statistics:")
            print(f"   Total sections: {len(sections)}")
            print(f"   Sections with punishment: {sum(1 for s in sections if s.get('punishment'))}")
            
            # Print sample
            print("\n📋 Sample section:")
            print(json.dumps(sections[0] if sections else {}, indent=2, ensure_ascii=False))
        else:
            print("❌ No sections extracted")
        
        return sections


def main():
    """Main execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Extract IPC sections from PDF")
    parser.add_argument("--use-llm", action="store_true", help="Use LLM for better accuracy (slower)")
    args = parser.parse_args()
    
    # Paths
    pdf_path = Path(__file__).parent.parent / "data" / "ipc" / "ipc_bare_act.pdf"
    output_path = Path(__file__).parent.parent / "data" / "ipc" / "ipc_sections.json"
    
    # Run extraction
    extractor = AdvancedIPCExtractor(str(pdf_path), use_llm=args.use_llm)
    sections = extractor.run(str(output_path))
    
    print(f"\n✨ Complete! Extracted {len(sections)} sections")
    print(f"📁 Output: {output_path}")


if __name__ == "__main__":
    main()
