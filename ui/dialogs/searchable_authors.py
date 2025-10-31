from .authors import AuthorsDialog
from .searchable_dialog import SearchableDialogMixin

class SearchableAuthorsDialog(AuthorsDialog, SearchableDialogMixin):
    def __init__(self, controller, parent=None):
        super().__init__(controller, parent)
        
    def setup_ui(self):
        super().setup_ui()
        self.init_search_components()
        self.setup_search()
        self.update_search_columns(self.author_table)
            
    def get_table_widget(self):
        return self.author_table