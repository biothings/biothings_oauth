class MultiDict(dict):
    """
    Provides multidict-type functionality to be used with WTForms.
    """
    def getlist(self, key):
        return self[key]

    def __repr__(self):
        return type(self).__name__ + '(' + dict.__repr__(self) + ')'
