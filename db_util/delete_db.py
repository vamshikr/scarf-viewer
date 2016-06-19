import pymongo

def main():
    client = pymongo.MongoClient()
    db = client['swamp']
    db['assessment_results'].drop()
    db['source_files'].drop()
    db['source_mapping'].drop()

if __name__ == '__main__':
	main()
