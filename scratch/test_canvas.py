import sys
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        if self._pageNumber == 1:
            # Skip cover page running headers
            return
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColorHex("#64748B")
        
        # Header
        self.drawString(36, 805, "Standard Operating Procedure: BMO Adverse Outcome Feedback Dashboard | DH Khargone")
        self.setStrokeColorHex("#CBD5E1")
        self.setLineWidth(0.5)
        self.line(36, 800, 559, 800)
        
        # Footer
        self.line(36, 42, 559, 42)
        self.drawString(36, 30, "National Health Mission - Khargone District (M.P.) | Adverse Pregnancy Outcome Audit")
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(559, 30, page_str)
        self.restoreState()

print("NumberedCanvas helper verified!")
