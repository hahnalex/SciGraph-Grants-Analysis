output_dir = '../out/grants_to_csv/'
id_file = output_dir + 'id.csv'                         # includes the IDs for grants, contributions, articles, and
                                                        #       SciGraph IDs
type_file = output_dir + 'type.csv'                     # includes the types of entries (grant or contribution)
funding_file = output_dir + 'funding.csv'               # includes funding amounts and funding currencies
metadata_file = output_dir + 'metadata.csv'             # includes languages, titles, abstracts, field of research
                                                        #       codes,  webpages, publications, and published names
year_file = output_dir + 'year.csv'                     # includes both start and end years
org_file = output_dir + 'org.csv'                       # includes both funding and recipient organizations
relationship_file = output_dir + 'relationship.csv'     # includes all triple relationships

nodes = set()
grid_database = {}

pred_types = set()


def proc_nt_file():
    with open("../data/springernature-scigraph-grants.2017-02-15.nt") as grants:
        for line in grants:
            line = line.rstrip(' .\n').split(' ', 2)

        # for x in range(0, 25):
        #     line = grants.readline().rstrip(' .\n').split(' ', 2)

            subj = line[0]
            pred = line[1]
            obj = line[2]

            subj_id = proc_subject(subj)
            pred_type = proc_predicate(pred)
            obj_id = proc_object(obj, pred_type)

            proc_relationship(subj_id, pred_type, obj_id)


def proc_subject(subj):
    subj = subj.strip('<>')
    subj = re.sub(r'http:\/\/www\.springernature\.com\/scigraph\/things\/', '', subj)
    subj_type = re.match(r'\w+', subj)
    subj_id = subj.split('/')[1]

    subj_label = None
    if subj_type.group(0) == 'grants':
        subj_label = 'grantID'
    elif subj_type.group(0) == 'contributions':
        subj_label = 'contributionID'

    if subj_label is not None:
        if subj_id not in nodes:
            with open(id_file, 'ab') as csv_file:
                id_writer = csv.writer(csv_file, delimiter=',')
                id_writer.writerow([subj_id, subj_label])
            nodes.add(subj_id)
    else:
        print "ERROR: could not process subject " + subj

    return subj_id


def proc_predicate(pred):
    pred = pred.strip('<>')
    pred_type = None

    if 'www.springernature.com' in pred:
        pred_type = re.sub(r'http:\/\/www\.springernature\.com\/scigraph\/ontologies\/core\/', '', pred)

    elif 'www.w3.org' in pred:
        pred_type = 'type'
    else:
        print "ERROR: could not process predicate " + pred

    return pred_type


def proc_object(obj, pred_type):
    obj = obj.strip('"<>')
    obj_id = None
    obj_file = None
    csv_row = None

    if pred_type == 'type':
        obj_id = re.sub(r'http:\/\/www\.springernature\.com\/scigraph\/ontologies\/core\/', '', obj)
        obj_file = type_file
        csv_row = [obj_id, 'type']

    elif pred_type == 'abstract':
        obj_id = obj
        obj_file = metadata_file
        csv_row = [obj_id, 'abstract']

    elif pred_type == 'endYear':
        obj_id = obj.split('"')[0]
        obj_file = year_file
        csv_row = [obj_id, 'endYear']

    elif pred_type == 'fundingAmount':
        obj_id = obj.split('"')[0]
        obj_file = funding_file
        csv_row = [obj_id, 'fundingAmount']

    elif pred_type == 'fundingCurrency':
        obj_id = obj
        obj_file = funding_file
        csv_row = [obj_id, 'fundingCurrency']

    elif pred_type == 'hasContribution':
        obj_id = re.sub(r'http:\/\/www\.springernature\.com\/scigraph\/things\/contributions\/', '', obj)
        obj_file = id_file
        csv_row = [obj_id, 'contributionID']

    elif pred_type == 'hasFieldOfResearchCode':
        obj_id = re.sub(r'http:\/\/purl\.org\/au\-research\/vocabulary\/anzsrc\-for\/2008\/', '' , obj)
        obj_file = metadata_file
        csv_row = [obj_id, 'fieldOfResearchCode']

    elif pred_type == 'hasFundedPublication':
        obj_id = re.sub(r'http:\/\/www\.springernature\.com\/scigraph\/things\/articles\/', '', obj)
        obj_file = id_file
        csv_row = [obj_id, 'articleID']

    elif pred_type == 'hasFundingOrganization':
        obj_id = re.sub(r'http:\/\/www\.grid\.ac\/institutes\/', '', obj)
        obj_file = org_file
        grid_lookup = grid_database.get(obj_id)

        if grid_lookup is None:
            grid_lookup = ['not found', 'not found', 'not found', 'not found']

        csv_row = [obj_id, grid_lookup[0], grid_lookup[1], grid_lookup[2], grid_lookup[3], 'fundingOrganization']

    elif pred_type == 'hasRecipientOrganization':
        obj_id = re.sub(r'http:\/\/www\.grid\.ac\/institutes\/', '', obj)
        obj_file = org_file
        grid_lookup = grid_database.get(obj_id)

        if grid_lookup is None:
            grid_lookup = ['not found', 'not found', 'not found', 'not found']

        csv_row = [obj_id, grid_lookup[0], grid_lookup[1], grid_lookup[2], grid_lookup[3], 'recipientOrganization']

    elif pred_type == 'language':
        obj_id = obj
        obj_file = metadata_file
        csv_row = [obj, 'language']

    elif pred_type == 'license':
        obj_id = obj
        obj_file = metadata_file
        csv_row = [obj, 'license']

    elif pred_type == 'publishedName':
        obj_id = obj
        obj_file = metadata_file
        csv_row = [obj_id, 'publishedName']

    elif pred_type == 'scigraphId':
        obj_id = obj
        obj_file = id_file
        csv_row = [obj_id, 'scigraphID']

    elif pred_type == 'startYear':
        obj_id = obj.split('"')[0]
        obj_file = year_file
        csv_row = [obj_id, 'startYear']

    elif pred_type == 'title':
        obj_id = obj
        obj_file = metadata_file
        csv_row = [obj_id, 'title']

    elif pred_type == 'webpage':
        obj_id = obj
        obj_file = metadata_file
        csv_row = [obj_id, 'webpage']

    else:
        print "ERROR: could not process object " + obj

    if obj_id is not None and obj_file is not None and csv_row is not None:
        if obj_id not in nodes:
            with open(obj_file, 'ab') as csv_file:
                id_writer = csv.writer(csv_file, delimiter=',')
                id_writer.writerow(csv_row)
            nodes.add(obj_id)
    else:
        print "ERROR: could not process object" + obj

    return obj_id


def proc_relationship(subj_id, pred_type, obj_id):
    with open(relationship_file, 'ab') as csv_file:
        rel_writer = csv.writer(csv_file, delimiter=',')
        rel_writer.writerow([subj_id, pred_type, obj_id])


def initialize_files():
    with open(funding_file, 'wb') as csv_file:
        scigraph_id_writer = csv.writer(csv_file, delimiter=',')
        scigraph_id_writer.writerow(['funding:ID', ':LABEL'])

    with open(id_file, 'wb') as csv_file:
        grant_writer = csv.writer(csv_file, delimiter=',')
        grant_writer.writerow(['thingID:ID', ':LABEL'])

    with open(metadata_file, 'wb') as csv_file:
        funding_amount_writer = csv.writer(csv_file, delimiter=',')
        funding_amount_writer.writerow(['metadata:ID', ':LABEL'])

    with open(org_file, 'wb') as csv_file:
        language_writer = csv.writer(csv_file, delimiter=',')
        language_writer.writerow(['gridID:ID', 'org', 'city', 'state', 'country', ':LABEL'])

    with open(relationship_file, 'wb') as csv_file:
        relationship_writer = csv.writer(csv_file, delimiter=',')
        relationship_writer.writerow([':START_ID', ':TYPE', ':END_ID'])

    with open(type_file, 'wb') as csv_file:
        type_writer = csv.writer(csv_file, delimiter=',')
        type_writer.writerow(['type:ID', ':LABEL'])

    with open(year_file, 'wb') as csv_file:
        funding_currency_writer = csv.writer(csv_file, delimiter=',')
        funding_currency_writer.writerow(['year:ID', ':LABEL'])


def load_grid_database():
    with open("../data/grid_database/grid.csv", "rb") as grid:
        grid_reader = csv.reader(grid, delimiter=",")
        for row in grid_reader:
            grid_database[row[0]] = [row[1], row[2], row[3], row[4]]


if __name__ == '__main__':
    import csv
    import re

    initialize_files()
    load_grid_database()
    proc_nt_file()
