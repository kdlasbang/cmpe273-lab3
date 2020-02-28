from ariadne import graphql_sync, make_executable_schema, ObjectType, gql
from ariadne.constants import PLAYGROUND_HTML
from flask import Flask, request, jsonify

type_defs = gql("""
type Query{
    students(id:Int!):Student
    classes(id:Int!):Class
}

type Mutation{
        addstudent(name:String!):String
        addclass(name:String!):String
        addStoC(sid:Int!, cid:Int!):Class
    }

type Student{
        id:Int! 
        name:String!
    }
type Class{ 
        id:Int!
        name:String!
        student:[Student]
    }

""")

students=[]
classes=[]
sid=0
cid=100

query = ObjectType("Query")
Mutation=ObjectType("Mutation")

@Mutation.field("addstudent")
def addstudent(_,info,name):
    global sid
    sid+=1
    students.append({'id':sid, 'name':name})
    return "added "+name

@Mutation.field("addclass")
def addclass(_,info,name):
    global cid
    cid+=1
    classes.append({'id':cid, 'name':name, 'student':[]})
    return "added "+name


@query.field("students")
def qstudent(_,info,id):
    for i in range(len(students)):
        if students[i]['id']==id:
            return students[i]
    return null# error 

@query.field("classes")
def qclass(_,info,id):
    for i in range(len(classes)):
        if classes[i]['id']==id:
            return classes[i]
    return null# error

@Mutation.field("addStoC")
def StoC(_,info,sid,cid):
    for ii in range(len(classes)):
        if classes[ii]['id']==cid:
            if len(classes[ii]['student'])==0:
                for z in range(len(students)):
                    if students[z]['id']==sid:
                        classes[ii]['student'].append(students[z])
                        return classes[ii]
            else:
                for j in range(len(students)):
                    if students[j]['id']==sid:
                        for k in range(len(classes[ii]['student'])):
                            if classes[ii]['student'][k]['id']==sid:
                                return classes[ii]
                            else:
                                continue
                        classes[ii]['student'].append(students[j])
                        return classes[ii]
    return null#error


schema = make_executable_schema(type_defs, query, Mutation)

app = Flask(__name__)


@app.route("/graphql", methods=["GET"])
def graphql_playgroud():
    # On GET request serve GraphQL Playground
    # You don't need to provide Playground if you don't want to
    # but keep on mind this will not prohibit clients from
    # exploring your API using desktop GraphQL Playground app.
    return PLAYGROUND_HTML, 200


@app.route("/graphql", methods=["POST"])
def graphql_server():
    # GraphQL queries are always sent as POST
    data = request.get_json()

    # Note: Passing the request to the context is optional.
    # In Flask, the current request is always accessible as flask.request
    success, result = graphql_sync(
        schema,
        data,
        context_value=request,
        debug=app.debug
    )

    status_code = 200 if success else 400
    return jsonify(result), status_code


if __name__ == "__main__":
    app.run(debug=True)
