class Company:
    def __init__(self, id=None, company_name=None, description=None, website=None, created_at=None):
        self.id = id
        self.company_name = company_name
        self.description = description
        self.website = website
        self.created_at = created_at

    def to_dict(self):
        return {
            'id': self.id,
            'company_name': self.company_name,
            'description': self.description,
            'website': self.website,
            'created_at': str(self.created_at) if self.created_at else None,
        }

    @classmethod
    def from_dict(cls, data):
        if not data:
            return None
        return cls(
            id=data.get('id'),
            company_name=data.get('company_name'),
            description=data.get('description'),
            website=data.get('website'),
            created_at=data.get('created_at')
        )
