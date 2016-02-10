{
    "insert":
    {
      "subject": "TACTIC: a new item has been added.",
      "message": '''
A new item has been added.
________________________
Code: {@GET(.code)}
Name: {@GET(.name)}
Description: {@GET(.description)}

    '''
    },


    # When an sobject has been updated
    "update":
    {
      "subject": "TACTIC: a new item has been updated.",
      "message": '''
An item has been added.
________________________
Code: {@GET(.code)}
Name: {@GET(.name)}
Description: {@GET(.description)}

    '''
    },


    # When a note has been added
    "insert|sthpw/note":
    {
        "subject": "TACTIC: a new note has been added.",
        "message": '''
A new note has been added.
_________________________

User: {@GET(.login)}
Note: {@GET(.note)}
        '''
    },



    # When a task has been assigned
    "change|sthpw/task|assigned":
    {
        "subject": "TACTIC: New task assignment {@GET(parent.code)} [{@GET(.context)}]",
        "message": '''
{@GET(parent.code)} has been assigned to you.
____________________________

Task: {@GET(.context)}
Assigned: {@GET(.assigned)}
Status: {@GET(.status)}
    '''
    },

    # When a task status has changed
    "change|sthpw/task|status":
    {
        "subject": "TACTIC: {@GET(parent.code)} [{@GET(.context)}] Updated to {@GET(.status)}",
        "message": '''
{@GET(parent.code)} has been updated.
____________________________

Task:{@GET(.context)}
Assigned: {@GET(.assigned)}
Status: {@GET(.status)}
        '''

    }

}
