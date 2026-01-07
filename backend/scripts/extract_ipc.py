"""
IPC PDF Extraction and Normalization Script
Extracts sections from IPC PDF and normalizes them into structured JSON format
"""

import re
import json
from pathlib import Path
from typing import List, Dict
import PyPDF2


class IPCExtractor:
    """Extract and normalize IPC sections from PDF"""
    
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.jurisdiction = "India"
        self.law = "IPC"
        
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
                    text += page.extract_text()
                    
        except Exception as e:
            print(f"❌ Error extracting PDF: {e}")
            raise
            
        print(f"✅ Extracted {len(text)} characters")
        return text
    
    def parse_sections(self, text: str) -> List[Dict]:
        """Parse IPC sections from extracted text"""
        print("\n🔍 Parsing IPC sections...")
        
        sections = []
        
        # Pattern to match IPC sections
        # Matches: "Section 420. Title.—Description text"
        # or "420. Title.—Description text"
        section_pattern = r'(?:Section\s+)?(\d+[A-Z]?)\.\s*([^.—]+?)\.?[—\-–]\s*(.*?)(?=(?:Section\s+)?\d+[A-Z]?\.|$)'
        
        matches = re.finditer(section_pattern, text, re.DOTALL | re.IGNORECASE)
        
        for match in matches:
            section_num = match.group(1).strip()
            title = match.group(2).strip()
            section_text = match.group(3).strip()
            
            # Clean up text
            section_text = re.sub(r'\s+', ' ', section_text)
            section_text = re.sub(r'\n+', ' ', section_text)
            
            if section_text and len(section_text) > 10:  # Basic validation
                sections.append({
                    "jurisdiction": self.jurisdiction,
                    "law": self.law,
                    "section": section_num,
                    "title": title,
                    "text": section_text
                })
        
        print(f"✅ Found {len(sections)} sections")
        return sections
    
    def parse_sections_alternative(self, text: str) -> List[Dict]:
        """
        Alternative parsing method using line-by-line approach
        Better for structured PDFs with consistent formatting
        """
        print("\n🔍 Parsing IPC sections (alternative method)...")
        
        sections = []
        lines = text.split('\n')
        
        current_section = None
        current_title = None
        current_text = []
        
        # Pattern for section header: "420." or "Section 420."
        section_header_pattern = r'^(?:Section\s+)?(\d+[A-Z]?)\.\s*(.+)$'
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if this is a section header
            match = re.match(section_header_pattern, line)
            
            if match:
                # Save previous section if exists
                if current_section and current_text:
                    sections.append({
                        "jurisdiction": self.jurisdiction,
                        "law": self.law,
                        "section": current_section,
                        "title": current_title,
                        "text": ' '.join(current_text).strip()
                    })
                
                # Start new section
                current_section = match.group(1).strip()
                current_title = match.group(2).strip()
                
                # Remove trailing dots or dashes from title
                current_title = re.sub(r'[.—\-–]+$', '', current_title).strip()
                current_text = []
                
            elif current_section:
                # Continue collecting text for current section
                current_text.append(line)
        
        # Save last section
        if current_section and current_text:
            sections.append({
                "jurisdiction": self.jurisdiction,
                "law": self.law,
                "section": current_section,
                "title": current_title,
                "text": ' '.join(current_text).strip()
            })
        
        print(f"✅ Found {len(sections)} sections")
        return sections
    
    def save_to_json(self, sections: List[Dict], output_path: str):
        """Save extracted sections to JSON file"""
        print(f"\n💾 Saving to {output_path}...")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(sections, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Saved {len(sections)} sections to JSON")
    
    def extract_and_normalize(self, output_path: str, use_alternative: bool = False) -> List[Dict]:
        """Complete extraction pipeline"""
        print("🚀 Starting IPC extraction pipeline...\n")
        
        # Extract text
        raw_text = self.extract_text_from_pdf()
        
        # Parse sections
        if use_alternative:
            sections = self.parse_sections_alternative(raw_text)
        else:
            sections = self.parse_sections(raw_text)
        
        # If no sections found with primary method, try alternative
        if not sections and not use_alternative:
            print("⚠️  No sections found with primary method, trying alternative...")
            sections = self.parse_sections_alternative(raw_text)
        
        # Save to JSON
        if sections:
            self.save_to_json(sections, output_path)
            
            # Print sample
            print("\n📋 Sample section:")
            print(json.dumps(sections[0], indent=2, ensure_ascii=False))
        else:
            print("❌ No sections extracted. Please check the PDF format.")
        
        return sections


def main():
    """Main execution function"""
    # Paths
    pdf_path = Path(__file__).parent.parent / "data" / "ipc" / "ipc_bare_act.pdf"
    output_path = Path(__file__).parent.parent / "data" / "ipc" / "ipc_sections.json"
    
    # Create extractor
    extractor = IPCExtractor(str(pdf_path))
    
    # Extract and normalize
    sections = extractor.extract_and_normalize(str(output_path))
    
    print(f"\n✨ Extraction complete! Total sections: {len(sections)}")
    print(f"📁 Output saved to: {output_path}")


if __name__ == "__main__":
    main()
