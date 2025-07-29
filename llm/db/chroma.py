import chromadb

class DBClient:
    def __init__(self, persist_dir = '/tmp/chroma'):
        self.client = chromadb.PersistentClient(path = persist_dir)
        try:
            self.collection = self.client.get_collection('contexts')
        except:
            self.collection = self.client.create_collection(name = 'contexts')

    def add_context(self, data):
        self.collection.add(**data)
        return self

    def query(self, query = None, n_results = 1, topic = None):
        if topic:
            return self.collection.query(query_texts = query, n_results = n_results, where = {'topic':topic}).get('documents')
        return self.collection.query(query_texts = query, n_results = n_results).get('documents')

    def get(self, topic = None):
        if topic:
            return self.collection.get(where = {'topic':topic})
        return self.collection.get()