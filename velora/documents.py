"""Local PDF/Word conversion. Never downloads content or follows document links."""
from __future__ import annotations
import html
import io
import os
import re
import zipfile
from pathlib import Path


def cancelled(cancel):
    if cancel and cancel.is_set():
        raise RuntimeError('Cancelled')


def pdf_to_word(src, out, cancel=None):
    import fitz
    from docx import Document
    from docx.shared import Inches, Pt
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    target = out / (src.stem + '.docx')
    result = Document()
    result.styles['Normal'].font.name = 'Arial'
    with fitz.open(src) as pdf:
        if pdf.needs_pass:
            raise ValueError('Password-protected PDFs must be unlocked before conversion.')
        if len(pdf) > 250:
            raise ValueError('Word export supports up to 250 PDF pages per file.')
        for i, page in enumerate(pdf):
            cancelled(cancel)
            if i:
                result.add_page_break()
            blocks = page.get_text('dict', sort=True)['blocks']
            has_text = any(b.get('type') == 0 and any(s.get('text', '').strip() for l in b.get('lines', []) for s in l.get('spans', [])) for b in blocks)
            if not has_text:
                pix = page.get_pixmap(matrix=fitz.Matrix(min(1.5, 1800/max(page.rect.width, page.rect.height)), min(1.5, 1800/max(page.rect.width, page.rect.height))), alpha=False)
                ratio = pix.width / pix.height
                width = min(6.2, 8.8 * ratio)
                result.add_picture(io.BytesIO(pix.tobytes('png')), width=Inches(width))
                continue
            for block in blocks:
                cancelled(cancel)
                if block.get('type') == 1:
                    width = min(6.2, 8.8 * block['width']/max(1, block['height']))
                    result.add_picture(io.BytesIO(block['image']), width=Inches(width))
                    continue
                for line in block.get('lines', []):
                    text = ''.join(s['text'] for s in line['spans'])
                    if not text.strip():
                        continue
                    p = result.add_paragraph()
                    is_rtl = bool(re.search(r'[\u0590-\u08ff]', text))
                    if is_rtl:
                        bidi = OxmlElement('w:bidi')
                        p._p.get_or_add_pPr().append(bidi)
                        p.alignment = 2
                    for span in line['spans']:
                        run = p.add_run(span['text'])
                        run.font.size = Pt(max(7, min(48, span['size'])))
                        run.bold = bool(span['flags'] & 16)
                        run.italic = bool(span['flags'] & 2)
                        if is_rtl:
                            rtl = OxmlElement('w:rtl')
                            run._r.get_or_add_rPr().append(rtl)
    cancelled(cancel)
    result.save(target)
    return [target]


def docx_to_pdf(src, out, cancel=None):
    """Basic PDF export without Office; preserves text, tables and inline images."""
    import fitz
    from docx import Document
    from docx.text.paragraph import Paragraph
    from docx.table import Table
    from docx.oxml.ns import qn
    # Reject archive expansion bombs before python-docx inflates the archive.
    with zipfile.ZipFile(src) as archive:
        if sum(i.file_size for i in archive.infolist()) > 150*1024*1024:
            raise ValueError('This Word document is too large to unpack.')
    document = Document(src)
    image_count = 0
    def paragraph(p):
        nonlocal image_count
        cancelled(cancel)
        text = p.text
        direction = 'rtl' if re.search(r'[\u0590-\u08ff]', text) else 'ltr'
        align = {0:'left', 1:'center', 2:'right', 3:'justify'}.get(p.alignment, 'right' if direction == 'rtl' else 'left')
        parts = []
        for run in (r for part in p.iter_inner_content() for r in ([part] if hasattr(part,'font') else part.runs)):
            value = html.escape(run.text).replace('\n', '<br/>')
            if run.bold:
                value = '<b>' + value + '</b>'
            if run.italic:
                value = '<i>' + value + '</i>'
            if run.underline:
                value = '<u>' + value + '</u>'
            size = run.font.size.pt if run.font.size else 12
            parts.append(f'<span style="font-size:{max(7,min(64,size))}pt">{value}</span>')
            for blip in run._r.xpath('.//a:blip'):
                rid = blip.get(qn('r:embed'))
                part = document.part.related_parts.get(rid)
                if not part:
                    continue
                # Only embedded image bytes. External relationships are never fetched.
                try:
                    pix = fitz.Pixmap(part.blob)
                    if pix.width*pix.height > 40_000_000:
                        raise ValueError('An embedded image exceeds 40 megapixels.')
                    name = f'word-image-{image_count}.png'
                    image_count += 1
                    pix.save(out/name)
                    parts.append(f'<img src="{name}" style="max-width:450pt;max-height:620pt"/>')
                except (RuntimeError, ValueError) as exc:
                    raise ValueError('A Word image could not be decoded. Use PNG or JPG images.') from exc
        content = ''.join(parts) or html.escape(text) or '&#160;'
        heading = p.style.name.lower().startswith('heading')
        tag = 'h2' if heading else 'p'
        breaks = 'page-break-before:always;' if p.paragraph_format.page_break_before else ''
        return f'<{tag} class="{direction}" style="text-align:{align};{breaks}">{content}</{tag}>'
    body = []
    for element in document.element.body:
        cancelled(cancel)
        if element.tag == qn('w:p'):
            body.append(paragraph(Paragraph(element, document)))
        elif element.tag == qn('w:tbl'):
            table = Table(element, document)
            body.append('<table>')
            for row in table.rows:
                body.append('<tr>')
                for cell in row.cells:
                    body.append('<td>' + ''.join(paragraph(p) for p in cell.paragraphs) + '</td>')
                body.append('</tr>')
            body.append('</table>')
    fonts = Path(__file__).resolve().parent.parent/'assets/fonts'
    archive = fitz.Archive(str(out))
    archive.add(str(fonts))
    css = '''@font-face{font-family:VeloraArabic;src:url(NotoSansArabic-Regular.ttf)}
    @font-face{font-family:VeloraArabic;src:url(NotoSansArabic-Bold.ttf);font-weight:bold}
    body{font-family:sans-serif;line-height:1.5;color:#111} .rtl{font-family:VeloraArabic,sans-serif}
    p{margin:0 0 8pt} table{border-collapse:collapse;width:100%;margin:10pt 0}
    td{border:0.5pt solid #ccc;padding:5pt;vertical-align:top} img{max-width:450pt;max-height:620pt}'''
    story = fitz.Story('<html><body>' + ''.join(body) + '</body></html>', user_css=css, archive=archive)
    target = out/(src.stem+'.pdf')
    def rectfn(number, filled):
        cancelled(cancel)
        if number >= 250:
            raise ValueError('Word to PDF supports up to 250 output pages.')
        return fitz.Rect(0,0,595,842), fitz.Rect(48,48,547,794), None
    writer = fitz.DocumentWriter(str(target))
    try:
        story.write(writer, rectfn)
    finally:
        writer.close()
    cancelled(cancel)
    raster_target = out / 'velora-rendered.pdf'
    with fitz.open(target) as rendered, fitz.open() as result:
        for page in rendered:
            cancelled(cancel)
            pix = page.get_pixmap(dpi=150, alpha=False)
            result.new_page(width=page.rect.width,height=page.rect.height).insert_image(page.rect,stream=pix.tobytes('jpg',jpg_quality=94))
        result.save(raster_target,deflate=True)
    os.replace(raster_target,target)
    return [target]
