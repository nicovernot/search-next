from app.models.logical_query import QueryRule, QueryGroup
from app.services.query_logic_parser import QueryLogicParser

def test_parser():
    # Test simple rule
    rule = QueryRule(field="title", operator="=", value="history")
    print(f"Simple Rule: {QueryLogicParser.to_solr_query(rule)}")

    # Test group
    group = QueryGroup(
        combinator="and",
        rules=[
            QueryRule(field="title", operator="contains", value="revolution"),
            QueryGroup(
                combinator="or",
                rules=[
                    QueryRule(field="author", operator="is", value="Hugo"),
                    QueryRule(field="author", operator="is", value="Zola"),
                ]
            )
        ]
    )
    print(f"Complex Group: {QueryLogicParser.to_solr_query(group)}")

    # Test NOT group
    not_group = QueryGroup(
        combinator="and",
        not_=True,
        rules=[QueryRule(field="type", operator="=", value="article")]
    )
    print(f"NOT Group: {QueryLogicParser.to_solr_query(not_group)}")

if __name__ == "__main__":
    test_parser()
