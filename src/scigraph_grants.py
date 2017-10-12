import csv
import logging
import operator
import re

grid_dictionary = {}
grants_per_state = {}

logging.basicConfig(filename='../out/errors.log', filemode='w', level=logging.WARNING)

with open("../data/grid_database/grid.csv", "rb") as grid:
    grid_reader = csv.reader(grid, delimiter=",")
    for row in grid_reader:
        grid_dictionary[row[0]] = [row[1], row[2], row[3], row[4]]

with open("../data/springernature-scigraph-grants.2017-02-15.nt") as grants:
    for line in grants:
        if "hasRecipientOrganization" in line:
            regex = re.search('grid\.[^ac]\d*\.\w*', line)

            if regex:
                recipient_org_id = regex.group(0)
                logging.info("Found " + recipient_org_id + " as recipient organization")

                grid_lookup = grid_dictionary.get(recipient_org_id)

                if grid_lookup is None:
                    logging.warning("GRID ID: " + recipient_org_id + " was found in the n-triple, but not found in the GRID DB")

                elif grid_lookup[3] == "United States":
                    recipient_state = grid_lookup[2]
                    logging.info(recipient_org_id + " recipient from State: " + recipient_state)

                    if grants_per_state.has_key(recipient_state):
                        grants_per_state[recipient_state] = grants_per_state.get(recipient_state) + 1
                    else:
                        grants_per_state[recipient_state] = 1
            else:
                logging.warning("Line in n-triple file includes \"hasRecipientOrganization\" but no GRID ID was found")

print
print "ALL STATES SORTED BY NUMBER OF GRANTS: "
print
sorted_by_grants = sorted(grants_per_state.items(), key=operator.itemgetter(1), reverse=True)
for entry in sorted_by_grants:
    print entry
print

# print
# print "ALL STATES SORTED ALPHABETICALLY: "
# print
# sorted_by_state = sorted(grants_per_state.items(), key=operator.itemgetter(0))
# for entry in sorted_by_state:
#     print entry
# print
