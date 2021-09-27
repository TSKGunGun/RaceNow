import factory
from factory import fuzzy
import string
from account.models import User, Organizer


class UserFactory(factory.django.DjangoModelFactory):
    username = factory.Faker('name', locale="ja-JP")
    email =factory.Faker('email', locale="ja-JP")
    
    class Meta:
        model = User

class OrganizerFactory(factory.django.DjangoModelFactory):

    owner = factory.SubFactory(UserFactory)
    name = factory.sequence(lambda n : u'主催団体_%d' % n )
    email_address = factory.Faker('company_email')
    url = factory.Faker('uri')
    
    @factory.post_generation
    def members(self, create, extracted, **kwargs):
        if not create: return
        if extracted:
            for member in extracted:
                self.members.add(member)

    class Meta:
        model = Organizer