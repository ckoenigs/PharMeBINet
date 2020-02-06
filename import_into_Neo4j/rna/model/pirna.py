from model.rna import RNA


class PiRNA(RNA):
    def __init__(self, ids: [str], names: [str]):
        super().__init__(ids, names)
        self.primary_id_prefix = 'HGNC'