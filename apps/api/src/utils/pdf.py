"""
Enhanced PDF Processing with OCR, Table Extraction, and Strict Page Boundaries
"""

import io
import logging
from typing import List, Dict, Any, Optional, Tuple
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import numpy as np
import re
from dataclasses import dataclass

from core.settings import Settings
from models.types import PageData, ChunkData, ImageDataModel, TableDataModel

logger = logging.getLogger(__name__)

@dataclass
class TableData:
    """Extracted table data"""
    page: int
    bbox: tuple  # (x0, y0, x1, y1)
    data: List[List[str]]
    headers: List[str]

@dataclass
class ImageData:
    """Extracted image data"""
    page: int
    bbox: tuple
    text: str  # OCR text
    confidence: float

class PDFProcessor:
    """Enhanced PDF processor with OCR, table extraction, and strict grounding"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.enable_ocr = settings.enable_tesseract
        self.tesseract_cmd = settings.tesseract_cmd or "/usr/bin/tesseract"
        
        if self.enable_ocr:
            pytesseract.pytesseract.tesseract_cmd = self.tesseract_cmd
    
    async def process_pdf(self, pdf_content: bytes, filename: str) -> List[PageData]:
        """Process PDF with strict page boundaries, OCR, and table extraction"""
        try:
            logger.info(f"Processing PDF: {filename}")
            
            # Open PDF
            doc = fitz.open(stream=pdf_content, filetype="pdf")
            pages_data = []
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                logger.info(f"Processing page {page_num + 1}/{len(doc)}")
                
                # Extract text with page boundaries
                page_text = page.get_text()
                
                # Extract images and run OCR
                images_data = await self._extract_images_with_ocr(page, page_num)
                
                # Extract tables
                tables_data = await self._extract_tables(page, page_num)
                
                # Create chunks with strict page boundaries
                chunks = await self._create_strict_chunks(
                    page_text, page_num, images_data, tables_data
                )
                
                # Extract spans and headings for compatibility
                spans = self._extract_spans(page)
                headings = self._extract_headings(page_text)
                slide_title = self._guess_slide_title(page_text, headings)
                preview_image = await self._generate_preview_image(page)
                
                # Convert ImageData dataclass objects to Pydantic models
                images_models = [
                    ImageDataModel(
                        page=img.page,
                        bbox=img.bbox,
                        text=img.text,
                        confidence=img.confidence
                    )
                    for img in images_data
                ]
                
                # Convert TableData dataclass objects to Pydantic models
                tables_models = [
                    TableDataModel(
                        page=table.page,
                        bbox=table.bbox,
                        data=table.data,
                        headers=table.headers
                    )
                    for table in tables_data
                ]
                
                # Create page data
                page_data = PageData(
                    page_number=page_num + 1,
                    text=page_text,
                    chunks=chunks,
                    spans=spans,
                    headings=headings,
                    slide_title_guess=slide_title,
                    preview_image=preview_image,
                    images=images_models,
                    tables=tables_models,
                    metadata={
                        "filename": filename,
                        "page_width": page.rect.width,
                        "page_height": page.rect.height,
                        "has_images": len(images_data) > 0,
                        "has_tables": len(tables_data) > 0
                    }
                )
                
                pages_data.append(page_data)
            
            doc.close()
            logger.info(f"Successfully processed {len(pages_data)} pages")
            return pages_data
            
        except Exception as e:
            logger.error(f"Failed to process PDF: {e}")
            raise
    
    async def _extract_images_with_ocr(self, page, page_num: int) -> List[ImageData]:
        """Extract images and run OCR on them"""
        images_data = []
        
        if not self.enable_ocr:
            return images_data
        
        try:
            # Get image list
            image_list = page.get_images()
            
            for img_index, img in enumerate(image_list):
                try:
                    # Get image data
                    xref = img[0]
                    pix = fitz.Pixmap(page.parent, xref)
                    
                    if pix.n - pix.alpha < 4:  # GRAY or RGB
                        # Convert to PIL Image
                        img_data = pix.tobytes("png")
                        pil_image = Image.open(io.BytesIO(img_data))
                        
                        # Run OCR
                        ocr_text = pytesseract.image_to_string(pil_image)
                        confidence = self._get_ocr_confidence(pil_image)
                        
                        if ocr_text.strip():
                            # Get image bounding box
                            img_rect = page.get_image_rects(xref)[0]
                            
                            image_data = ImageData(
                                page=page_num + 1,
                                bbox=(img_rect.x0, img_rect.y0, img_rect.x1, img_rect.y1),
                                text=ocr_text.strip(),
                                confidence=confidence
                            )
                            images_data.append(image_data)
                            
                            logger.info(f"OCR extracted text from image {img_index + 1}: {len(ocr_text)} chars")
                    
                    pix = None
                    
                except Exception as e:
                    logger.warning(f"Failed to process image {img_index + 1}: {e}")
                    continue
                    
        except Exception as e:
            logger.warning(f"Failed to extract images from page {page_num + 1}: {e}")
        
        return images_data
    
    async def _extract_tables(self, page, page_num: int) -> List[TableData]:
        """Extract tables from page"""
        tables_data = []
        
        try:
            # Find tables using PyMuPDF's table detection
            tables = page.find_tables()
            
            for table_index, table in enumerate(tables):
                try:
                    # Extract table data
                    table_data = table.extract()
                    
                    if table_data and len(table_data) > 1:  # Has headers and data
                        headers = table_data[0] if table_data else []
                        data = table_data[1:] if len(table_data) > 1 else []
                        
                        # Get table bounding box
                        bbox = table.bbox
                        
                        table_info = TableData(
                            page=page_num + 1,
                            bbox=bbox,
                            data=data,
                            headers=headers
                        )
                        tables_data.append(table_info)
                        
                        logger.info(f"Extracted table {table_index + 1}: {len(data)} rows")
                        
                except Exception as e:
                    logger.warning(f"Failed to extract table {table_index + 1}: {e}")
                    continue
                    
        except Exception as e:
            logger.warning(f"Failed to extract tables from page {page_num + 1}: {e}")
        
        return tables_data
    
    async def _create_strict_chunks(
        self, 
        page_text: str, 
        page_num: int, 
        images_data: List[ImageData], 
        tables_data: List[TableData]
    ) -> List[ChunkData]:
        """Create chunks with strict page boundaries and multimodal content"""
        chunks = []
        
        # Split text into sentences for better chunking
        sentences = self._split_into_sentences(page_text)
        
        # Create text chunks
        current_chunk = ""
        chunk_sentences = []
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) > 500:  # Max chunk size
                if current_chunk.strip():
                    chunk = ChunkData(
                        chunk_id=f"page_{page_num + 1}_text_{len(chunks)}",
                        text=current_chunk.strip(),
                        page=page_num + 1,
                        chunk_type="text",
                        metadata={
                            "sentences": chunk_sentences,
                            "word_count": len(current_chunk.split()),
                            "char_count": len(current_chunk)
                        }
                    )
                    chunks.append(chunk)
                
                current_chunk = sentence
                chunk_sentences = [sentence]
            else:
                current_chunk += " " + sentence
                chunk_sentences.append(sentence)
        
        # Add final chunk
        if current_chunk.strip():
            chunk = ChunkData(
                chunk_id=f"page_{page_num + 1}_text_{len(chunks)}",
                text=current_chunk.strip(),
                page=page_num + 1,
                chunk_type="text",
                metadata={
                    "sentences": chunk_sentences,
                    "word_count": len(current_chunk.split()),
                    "char_count": len(current_chunk)
                }
            )
            chunks.append(chunk)
        
        # Create image chunks
        for img_data in images_data:
            if img_data.text.strip():
                chunk = ChunkData(
                    chunk_id=f"page_{page_num + 1}_image_{img_data.page}",
                    text=f"[IMAGE] {img_data.text}",
                    page=page_num + 1,
                    chunk_type="image",
                    metadata={
                        "bbox": img_data.bbox,
                        "confidence": img_data.confidence,
                        "ocr_text": img_data.text
                    }
                )
                chunks.append(chunk)
        
        # Create table chunks
        for table_data in tables_data:
            table_text = self._format_table_text(table_data)
            if table_text.strip():
                chunk = ChunkData(
                    chunk_id=f"page_{page_num + 1}_table_{table_data.page}",
                    text=f"[TABLE] {table_text}",
                    page=page_num + 1,
                    chunk_type="table",
                    metadata={
                        "bbox": table_data.bbox,
                        "headers": table_data.headers,
                        "rows": len(table_data.data),
                        "table_data": table_data.data
                    }
                )
                chunks.append(chunk)
        
        logger.info(f"Created {len(chunks)} chunks for page {page_num + 1}")
        return chunks
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _format_table_text(self, table_data: TableData) -> str:
        """Format table data as readable text"""
        if not table_data.data:
            return ""
        
        text_parts = []
        
        # Add headers
        if table_data.headers:
            text_parts.append("Headers: " + " | ".join(table_data.headers))
        
        # Add data rows
        for row in table_data.data[:5]:  # Limit to first 5 rows
            if row:
                text_parts.append(" | ".join(str(cell) for cell in row))
        
        return "\n".join(text_parts)
    
    def _get_ocr_confidence(self, image: Image.Image) -> float:
        """Get OCR confidence score"""
        try:
            # Get confidence data
            data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
            confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
            
            if confidences:
                return sum(confidences) / len(confidences) / 100.0  # Normalize to 0-1
            
            return 0.0
            
        except Exception:
            return 0.0
    
    def _extract_spans(self, page) -> List[Dict[str, Any]]:
        """Extract text spans with bounding boxes"""
        spans = []
        
        try:
            # Get text blocks
            blocks = page.get_text("dict")
            
            for block in blocks["blocks"]:
                if "lines" in block:
                    for line in block["lines"]:
                        for span in line["spans"]:
                            spans.append({
                                "text": span["text"],
                                "bbox": span["bbox"],
                                "font": span["font"],
                                "size": span["size"]
                            })
            
        except Exception as e:
            logger.error(f"Failed to extract spans: {e}")
        
        return spans
    
    def _extract_headings(self, text: str) -> List[str]:
        """Extract potential headings from text"""
        headings = []
        
        try:
            lines = text.split('\n')
            
            for line in lines:
                line = line.strip()
                
                # Check if line looks like a heading
                if self._is_heading(line):
                    headings.append(line)
            
        except Exception as e:
            logger.error(f"Failed to extract headings: {e}")
        
        return headings
    
    def _is_heading(self, line: str) -> bool:
        """Check if line looks like a heading"""
        if not line or len(line) < 3:
            return False
        
        # Common heading patterns
        patterns = [
            r'^\d+\.?\s+[A-Z]',  # Numbered headings
            r'^[A-Z][A-Z\s]+$',  # All caps
            r'^[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*$',  # Title case
            r'^#{1,6}\s+',  # Markdown headings
            r'^[A-Z][a-z]+:$',  # Colon endings
        ]
        
        for pattern in patterns:
            if re.match(pattern, line):
                return True
        
        return False
    
    def _guess_slide_title(self, text: str, headings: List[str]) -> Optional[str]:
        """Guess slide title from text and headings"""
        if not headings:
            return None
        
        # Use first heading as title
        return headings[0]
    
    async def _generate_preview_image(self, page) -> bytes:
        """Generate preview image for page"""
        try:
            # Render page as image
            mat = fitz.Matrix(144/72, 144/72)  # 144 DPI
            pix = page.get_pixmap(matrix=mat)
            
            # Convert to bytes
            img_data = pix.tobytes("png")
            
            return img_data
            
        except Exception as e:
            logger.error(f"Failed to generate preview image: {e}")
            return b""
    
    def chunk_page(self, page_data: PageData, page_num: int) -> List[ChunkData]:
        """Chunk page into smaller pieces (legacy method for compatibility)"""
        return page_data.chunks
