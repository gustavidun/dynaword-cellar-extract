from SPARQLWrapper import SPARQLWrapper, JSON
import polars as pl

def iter_month_ranges(start_year, end_year):
    for year in range(start_year, end_year + 1):
        for month in range(1, 13):
            start = f"{year}-{month:02d}-01"
            
            if month == 12:
                end = f"{year+1}-01-01"
            else:
                end = f"{year}-{month+1:02d}-01"
            
            yield year, month, start, end

def fetch_metadata():
    sparql = SPARQLWrapper("https://publications.europa.eu/webapi/rdf/sparql")

    for year, month, start, end in iter_month_ranges(2022, 2026):

        query = f"""
            PREFIX cdm: <http://publications.europa.eu/ontology/cdm#>
            PREFIX purl: <http://purl.org/dc/elements/1.1/>

            SELECT ?item ?langCode ?type ?date
            WHERE {{
                ?work cdm:date_creation_legacy ?date ;
                        a ?class .

                ?expr cdm:expression_belongs_to_work ?work ;
                        cdm:expression_uses_language ?lang .

                ?lang purl:identifier ?langCode .

                ?manif cdm:manifestation_manifests_expression ?expr ;
                        cdm:manifestation_type ?type .

                ?item cdm:item_belongs_to_manifestation ?manif .

                FILTER(?date >= "{start}"^^xsd:date &&
                ?date < "{end}"^^xsd:date)
            }}
            ORDER BY ?item
            """    
        
        try:
            sparql.setQuery(query)
            sparql.setReturnFormat(JSON)
            results = sparql.query().convert()
        except Exception as e: 
            print(e)
            break
        
        if not results:
            print(f"No results found in {year}/{month}.")
        else:
            print(f"{len(results["results"]["bindings"])} found in {year}/{month}")
            yield results, year, month

def serialize_results(results):
    rows = [
        {
            "item": r["item"]["value"],
            "langCode": r["langCode"]["value"],
            "type": r["type"]["value"],
            "date": r["date"]["value"]
        }
        for r in results["results"]["bindings"]        
    ]
    return rows

if __name__ == "__main__":
    buffer = []
    for r, y, m in fetch_metadata():
        df = pl.DataFrame(serialize_results(r))
        df.write_parquet(f"metadata/meta_{y}-{m}.parquet")

