# biothings_oauth

## Setup 


 1. Install Elasticsearch 6.x:

        docker run -d -p 9200:9200 -p 9300:9300 -e "discovery.type=single-node" --name elasticsearch docker.elastic.co/elasticsearch/elasticsearch:6.8.13
        
 2. Install Python dependencies:
      
        python install -r requirements.txt

 3. Load the demo Elasticsearch index:
     
        npm install elasticdump -g
        elasticdump --input=mygeneset_analyzer_v0.1.json  --output=http://localhost:9200/test_build_01_20201029_hddqb05m --type=analyzer
        elasticdump --input=mygeneset_mapping_v0.1.json  --output=http://localhost:9200/test_build_01_20201029_hddqb05m --type=mapping
        elasticdump --input=mygeneset_index_v0.1.json  --output=http://localhost:9200/test_build_01_20201029_hddqb05m --type=data
 
 4. set the Elasticsearch index alias:
 
        curl -X POST "localhost:9200/_aliases?pretty" -H 'Content-Type: application/json' -d'
        {
            "actions" : [
                { "add" : { "index" : "test_build_01_20201029_hddqb05m", "alias" : "mygeneset_current" } }
            ]
        }
        '

## Run the web API server

    python index.py --conf=config_web --debug
