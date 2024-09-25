from flask import Flask, request, jsonify
import sqlite3
from database import read, get_member_by_id, update_member_github_username, delete_member
import requests

app = Flask(__name__)

# GET
# Route to read all members
@app.route("/members", methods=['GET'])
def read_all():
    return jsonify(read())

# GET
# Route to read one member by id
@app.route("/members/<int:id>", methods=['GET'])
def get_one_member(id):
    # Call the function to get a member by id
    member = get_member_by_id(id)
    
    # Error handling
    if member:
        return jsonify(member), 200  
    else:
        return jsonify({"error": "Member not found"}), 404  


# PUT
# Route to update github_username of a member by id endpoint
# Could be done by using an id in the JSON body instead of the URL depends on preference
@app.route("/members/<int:id>/change_github_username", methods=['PUT'])
def update_github_username(id):
    # Extract the JSON data from the request body
    data = request.json  # Expecting JSON data in the request body
    # Check if the JSON data contains a github_username
    new_github_username = data.get('github_username')
    # If no github_username is provided, return an error message and status code 400
    if not new_github_username:
        return jsonify({"error": "No github_username provided"}), 400  

    # Call the function to update the database
    updated = update_member_github_username(id, new_github_username)

    # Error handling
    if updated:
        return jsonify({"message": f"Username updated successfully to: {new_github_username}"}), 200
    else:
        return jsonify({"error": "Member not found"}), 404  
   

# GET
# Route to fetch id and github_username of all members
@app.route("/members/github_usernames", methods=['GET'])
def get_github_usernames():
    with sqlite3.connect('members.db') as conn:
        cur = conn.cursor()
        cur.execute('SELECT id, github_username FROM members')
        conn.commit()

        members = []
        for i in cur.fetchall():
            members.append({"id": i[0], "github_username": i[1]})
        
        # Error handling
        if not members:
            return jsonify({"error": "No members found"}), 404

    return members

# GET using Github API
# Route to fetch github repos on usernames list
@app.route("/members/github_repos", methods=['GET'])
def get_repos_list():
    # Get the list of members with their github usernames and ids
    members = get_github_usernames()  
    # Loop through the members and fetch their individual repos
    for member in members:
        username = member['github_username']
        
        # Fetch the user's repos using the Github API
        response = requests.get(f"https://api.github.com/users/{username}/repos")

        if response.status_code == 200:
            # Extract repo names from the response if the request is successful
            repos = [repo['name'] for repo in response.json()]
            # Add the repos to the member's dictionary  
            member['repos'] = repos  
        else:
            # If the request fails, add an empty list to the member's dictionary
            member['repos'] = []

    return jsonify(members)

# GET using Github API
# Route to fetch github repos on a specific username and using a github token in the header
@app.route("/members/<int:id>/github_repos", methods=['GET'])
def get_repos_by_id(id):
    # Get the member by id
    member = get_member_by_id(id)
    
    # Stop the function if the member is not found
    if not member:
        return jsonify({"error": "Member not found"}), 404
    
    # Get the github username of the member
    username = member['github_username']
    
    # Get the token from the header
    token = request.headers.get('Authorization')
    
    # Stop the function if no token is provided
    if not token:
        return jsonify({"error": "No token provided"}), 401
    
    # Add the token to the headers
    headers = {"Authorization": f"token {token}"}
    
    # Fetch the user's repos using the Github API
    response = requests.get(f"https://api.github.com/users/{username}/repos", headers=headers)
    print(response.status_code)
    print(response.json())
    if response.status_code == 200:
        # Extract repo names from the response if the request is successful
        repos = [repo['name'] for repo in response.json()]
        # Add the repos to the member's dictionary
        member['repos'] = repos
    else:
        member['repos'] = []

    return jsonify(member), 200

# DELETE
# Route to delete a member by id
@app.route("/members/<int:id>/delete", methods=['DELETE'])
def delete_member_by_id(id):
    
    deleted = delete_member(id)
    
    # Error handling
    if deleted:
        return jsonify({"message": f"Member with id {id} deleted"}), 200
    else:
        return jsonify({"error": "Member not found"}), 404

app.run(debug=True)



