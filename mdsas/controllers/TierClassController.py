import sqlalchemy as db
from sqlalchemy import select, update, insert, and_, delete
from sqlalchemy.engine import CursorResult

from settings import settings


class TierClassController:
    TIERCLASS = None
    TIERASSIGNMENT = None

    def __init__(self, metadata, engine, connection, algorithms):
        self.METADATA = metadata
        self.ENGINE = engine
        self.CONNECTION = connection
        self.algorithms = algorithms

        self._set_tierclass_table()
        # self._set_tierassignment_table()

    def _execute_query(self, query):
        resultProxy: CursorResult = self.CONNECTION.execute(query)
        queryResult = resultProxy.fetchall()
        rows = [row._asdict() for row in queryResult]

        return rows

    def _set_tierclass_table(self):
        self.TIERCLASS = db.Table(
            settings.TIERCLASS, self.METADATA, autoload=True, autoload_with=self.ENGINE
        )

    # def _set_tierassignment_table(self):
    #     self.TIERASSIGNMENT = db.Table(
    #         settings.TIERASSIGNMENT, self.METADATA, autoload=True, autoload_with=self.ENGINE
    #     )

    def get_tierclass_by_id(self, payload):
        query = select([self.TIERCLASS]).where(
            self.TIERCLASS.columns.tierClassID == payload['tierClassID']
        )
        rows = self._execute_query(query)

        if len(rows) > 0:
            return {
                'status': 1,
                'tierClass': rows[0]
            }

        return {
            'status': 0,
            'message': "No tier classes"
        }

    def get_tierclass(self):
        query = select([self.TIERCLASS])
        rows = self._execute_query(query)

        if len(rows) > 0:
            return {
                'status': 1,
                'tierClasses': rows
            }

        return {
            'status': 0,
            'message': "No tier classes"
        }

    def create_tierclass(self, payload):
        tierClassName = payload['tierClassName']
        tierPriorityLevel = payload['tierPriorityLevel']
        tierClassDescription = payload['tierClassDescription']
        maxTierNumber = payload['maxTierNumber']
        tierUpperBand = payload['tierUpperBand']
        tierLowerBand = payload['tierLowerBand']

        query = select([self.TIERCLASS]).where(self.TIERCLASS.columns.tierClassName == tierClassName)
        rows = self._execute_query(query)
        if len(rows) > 0:
            return {
                "status": 0,
                "exists": 1,
                "message": f"Tier Class '{tierClassName}' already exists."
            }

        insertQuery = insert(self.TIERCLASS).values(
            tierClassName=tierClassName, tierPriorityLevel=tierPriorityLevel,
            tierClassDescription=tierClassDescription, maxTierNumber=maxTierNumber,
            tierUpperBand=tierUpperBand, tierLowerBand=tierLowerBand
        )
        ResultProxy = self.CONNECTION.execute(insertQuery)

        rows = self._execute_query(query)
        if len(rows) < 1:
            return {
                "status": 0,
                "message": "Tier Class could not be added. Contact an administrator."
            }

        return {
            "status": 1,
            "message": "Tier Class has been added."
        }

    def update_tierclass(self, payload):
        tierClassName = payload['tierClassName']
        tierPriorityLevel = payload['tierPriorityLevel']
        tierClassDescription = payload['tierClassDescription']
        maxTierNumber = payload['maxTierNumber']
        tierUpperBand = payload['tierUpperBand']
        tierLowerBand = payload['tierLowerBand']

        if not tierClassName or not tierPriorityLevel or not maxTierNumber or not tierUpperBand or not tierLowerBand:
            raise Exception("All parameters not provided")

        updateQuery = update(self.TIERCLASS).values(
            tierClassName=tierClassName, tierPriorityLevel=tierPriorityLevel,
            tierClassDescription=tierClassDescription, maxTierNumber=maxTierNumber,
            tierUpperBand=tierUpperBand, tierLowerBand=tierLowerBand
        ).where(
            self.TIERCLASS.columns.tierClassName == tierClassName
        )
        rows = self._execute_query(updateQuery)

        return {
            "status": 1,
            "message": "Tier Class has been updated."
        }

    # ---- Tier Class Assignment to Nodes is done at node creation
    #
    # def create_tierclass_assignment(self, payload):
    #     query = select([self.TIERASSIGNMENT]).where(
    #         self.TIERASSIGNMENT.columns.secondaryUserID == payload['secondaryUserID']
    #     )
    #
    #     rows = self._execute_query(query)
    #     if len(rows) > 0:
    #         return {
    #             "status": 0,
    #             "exists": 1,
    #             "message": f"Tier Assignment for {payload['secondaryUserID']} already exists."
    #         }
    #
    #     insertQuery = insert(self.TIERASSIGNMENT).values(
    #         tierClassID=payload['tierClassID'],
    #         secondaryUserID=payload['secondaryUserID'],
    #         innerTierLevel=payload['innerTierLevel']
    #     )
    #     ResultProxy = self.CONNECTION.execute(insertQuery)
    #
    #     rows = self._execute_query(query)
    #     if len(rows) < 1:
    #         return {
    #             "status": 0,
    #             "message": "Tier Assignment could not be added. Contact an administrator."
    #         }
    #
    #     return {
    #         "status": 1,
    #         "message": "Tier Assignment has been added."
    #     }
    #
    # def alter_tierclass_assignment(self, payload):
    #     isNewTA = payload['isNewTA']
    #     secondaryUserID = payload['secondaryUserID']
    #     tierClassID = payload['tierClassID']
    #     innerTierLevel = payload['innerTierLevel']
    #     tierAssignmentID = ""
    #
    #     if not secondaryUserID or not tierClassID or not innerTierLevel:
    #         raise Exception("Parameters not provided")
    #
    #     if not isNewTA:
    #         tierAssignmentID = payload['tierAssignmentID']
    #         if not tierAssignmentID:
    #             raise Exception("Parameters not provided")
    #
    #     query = select([self.TIERASSIGNMENT]).where(and_(
    #         self.TIERASSIGNMENT.columns.secondaryUserID == secondaryUserID,
    #         self.TIERASSIGNMENT.columns.tierClassID == tierClassID
    #     ))
    #
    #     rows = self._execute_query(query)
    #     if len(rows) > 0:
    #         # Update
    #         updateQuery = update(self.TIERASSIGNMENT).values(
    #             tierClassID=tierClassID, secondaryUserID=secondaryUserID, innerTierLevel=innerTierLevel
    #         ).where(
    #             self.TIERASSIGNMENT.columns.tierAssignmentID == tierAssignmentID
    #         )
    #         rows = self._execute_query(updateQuery)
    #
    #         return {
    #             'status': 1,
    #             'message': "Tier class updated successfully"
    #         }
    #     else:
    #         # Create
    #         insertQuery = insert(self.TIERASSIGNMENT).values(
    #             tierClassID=tierClassID, secondaryUserID=secondaryUserID, innerTierLevel=innerTierLevel
    #         )
    #         rows = self._execute_query(insertQuery)
    #
    #         return {
    #             'status': 1,
    #             'message': "Tier class created successfully"
    #         }
    #
    # def get_tireclass_assignment_by_id(self, payload):
    #     if 'tierClassID' not in payload:
    #         raise Exception('tierClassID not provided')
    #
    #     query = select([self.TIERASSIGNMENT]).where(
    #         self.TIERASSIGNMENT.columns.tierClassID == payload['tierClassID']
    #     )
    #     rows = self._execute_query(query)
    #
    #     if len(rows) > 0:
    #         return {
    #             'status': 1,
    #             'tierClass': rows[0]
    #         }
    #
    #     return {
    #         'status': 0,
    #         'message': "No tier classes"
    #     }
    #
    # def delete_tierclass_assignment(self, payload):
    #     assignmentID = payload.get('assignmentID', None)
    #     if not assignmentID:
    #         raise Exception('Assignment ID not provided')
    #
    #     query = delete([self.TIERASSIGNMENT]).where(
    #         self.TIERASSIGNMENT.columns.tierAssignmentID == assignmentID
    #     ).first()
    #     rows = self._execute_query(query)
    #
    #     return {
    #         'status': 0,
    #         'message': f"Tier Assignment {assignmentID} deleted"
    #     }

    def load_seed_data(self):
        self.create_tierclass(
            self.generate_seed_payload('Tier1', 0, 'Tier1 - Top Level', 2, 15e8, 12e8)
        )
        self.create_tierclass(
            self.generate_seed_payload('Tier2', 1, 'Tier2 - Middle Level', 5, 17e8, 14e8)
        )
        self.create_tierclass(
            self.generate_seed_payload('Tier3', 2, 'Tier3 - Low Level', 9, 19e8, 15e8)
        )

        # self.create_tierclass_assignment({'tierClassID': 1, 'secondaryUserID': 'abc', 'innerTierLevel': 1})
        # self.create_tierclass_assignment({'tierClassID': 2, 'secondaryUserID': 'bbc', 'innerTierLevel': 1})
        # self.create_tierclass_assignment({'tierClassID': 3, 'secondaryUserID': 'cbc', 'innerTierLevel': 1})

    @staticmethod
    def generate_seed_payload(name, priority, description, maxTiers, upperBand, lowerBand):
        return {
            'tierClassName': name,
            'tierPriorityLevel': priority,
            'tierClassDescription': description,
            'maxTierNumber': maxTiers,
            'tierUpperBand': upperBand,
            'tierLowerBand': lowerBand
        }
