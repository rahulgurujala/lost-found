# URL template with placeholders for parameters
URL_TEMPLATE = (
    "https://mumbaipolice.gov.in/Lostfoundarticle?"
    "complaint_type={complaint_type}&"
    "article_type={article_type}&"
    "article_desc={article_desc}&"
    "page={page}"
)

# Example usage with the Pydantic model:
# from models import SearchParams, ComplaintType, ArticleType
#
# # Create search parameters
# params = SearchParams(
#     complaint_type=ComplaintType.LOST_ITEM,
#     article_type=ArticleType.PAN_CARD,
#     article_desc="My PAN Card",
#     page=1
# )
#
# # Generate URL
# url = URL_TEMPLATE.format(**params.to_dict())
