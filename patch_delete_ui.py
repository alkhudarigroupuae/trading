import re

file_path = '/Users/mac/Documents/trae_projects/TradeEngine/templates/settings.html'
with open(file_path, 'r') as f:
    content = f.read()

old_delete = """function deleteAccount(id) {
    if (confirm('Are you sure you want to delete this account?')) {
        showAlert('Account deleted successfully', 'success');
        loadAccountsList();
    }
}"""

new_delete = """function deleteAccount(id) {
    if (confirm('Are you sure you want to delete this account permanently?')) {
        fetch(`/api/accounts/${id}`, {
            method: 'DELETE'
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                showAlert('Error deleting account: ' + data.error, 'danger');
            } else {
                showAlert('Account deleted successfully', 'success');
                loadAccountsList();
            }
        })
        .catch(error => {
           import re

file_path = '/Users/mac/Documents/trae_projects/TradeEngine/templates/settinge
file_pa   with open(file_path, 'r') as f:
    content = f.read()

old_delete = """function dee,    content = f.read()

old_dee_
old_delete = """func       if (confirm('Are you sure you want to dgs        showAlert('Account de.")
else:
    print("Could not find del        loadAccountsList();
    }
}"")
