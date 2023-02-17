import pdf_tools


class SearchPdfs(pdf_tools.PdfTool):
    def __init__(self, input_path, output_path, df_search):
        self.df_search = df_search
        super().__init__(input_path, output_path)
