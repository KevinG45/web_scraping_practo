import scrapy

class DoctorItem(scrapy.Item):
    name = scrapy.Field()
    specialization = scrapy.Field()
    experience = scrapy.Field()
    qualifications = scrapy.Field()
    clinics = scrapy.Field()
    fees = scrapy.Field()
    rating = scrapy.Field()
    reviews_count = scrapy.Field()
    services = scrapy.Field()
    address = scrapy.Field()
    google_maps_link = scrapy.Field()
    phone = scrapy.Field()
    availability = scrapy.Field()
    profile_url = scrapy.Field()
    image_url = scrapy.Field()