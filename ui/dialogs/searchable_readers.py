from .readers import ReadersDialog
from .searchable_dialog import SearchableDialogMixin

class SearchableReadersDialog(ReadersDialog, SearchableDialogMixin):
    def __init__(self, controller, parent=None):
        super().__init__(controller, parent)
        
    def setup_ui(self):
        super().setup_ui()
        self.init_search_components()
        self.setup_search()
        self.update_search_columns(self.readers_table)
            
    def get_table_widget(self):
        return self.readers_table