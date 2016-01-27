"""""

stats.py 

Brief: uses MongoDB to run statistics on the JSON dataset.

Ronald Rihoo

"""""

def initialize_db(db_name):
    from pymongo import MongoClient
    client = MongoClient('localhost:27017')
    db = client[db_name]
    return db

# sort = 1 or -1
def mongo_pipeline(db, task, value = '', key = 'type', group = '', sort = 1, limit = 1):
    # mongo_pipeline(db, 'count distincts', 'created.user' )
    if task == 'count distincts':
        return len(db.dallas.distinct(value))
    # mongo_pipeline(db, 'count found', 'node' )
    if task == 'count findings':
        if value != '':
            return db.dallas.find( { key : value } ).count()
        return db.dallas.find().count()                                               # count of the documents
    # mongo_pipeline(db, 'aggregate', 'amenity')
    if task == 'group count':
        pipeline =  [ { '$group' : { '_id' : '$'+value, 
                                     'count' : { '$sum' : 1 } } }, 
                      { '$sort' : { 'count' : sort } }, 
                      { '$limit' : limit } 
                    ]
        return [doc for doc in db.dallas.aggregate( pipeline )]
    if task == 'match then count unique group':
        pipeline = [ { '$match' : { key : value }},
                     { '$group' : { '_id' : '$'+group,
                                    'unique' : { '$addToSet' : '$'+group }}},
                     { '$unwind' : '$unique' },
                     { '$group' : { '_id' : '$'+group,
                                    'count' : { '$sum' : 1 }}},
                   ]
        return [doc for doc in db.dallas.aggregate( pipeline )][0]['count']
    if task == 'match to user':
        pipeline = [ { '$match' : { key : value }},
                     { '$group' : { '_id' : '$created.user', 
                                     'count' : { '$sum' : 1 }}}, 
                     { '$sort' : { '_id' : sort }},
                   ]
        #return pipeline
        return [doc for doc in db.dallas.aggregate( pipeline )]
    return pipeline

def run_stats():
    db = initialize_db('map')
     
    stats = {}

    stats['document count'] = mongo_pipeline(db, 'count findings')
    stats['unique users'] = mongo_pipeline(db, 'count distincts', 'created.user')
    stats['node count'] = mongo_pipeline(db, 'count findings', 'node')
    stats['way count'] = mongo_pipeline(db, 'count findings', 'way')
    stats['distinct amenities'] = mongo_pipeline(db, 'count distincts', 'amenity')
    stats['restaurant count'] = mongo_pipeline(db, 'count findings', 'restaurant', 'amenity')
    stats['unique restaurants'] = mongo_pipeline(db, 'match then count unique group', 'restaurant', 'amenity', 'name')

    import pprint
    pprint.pprint(stats)

run_stats()