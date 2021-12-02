import requests

DNS = input("Digite o DNS ")
endpoint = int(input(
    "O que você quer fazer um: \n 1 - GET \n 2 - POST \n 3 - DELETE \nResposta: "))

if endpoint == 3:
    id_del = input("Qual ID você quer deletar? ")
elif endpoint == 2:
    title = input("Qual título de sua tarefa? ")
    date = input("Qual a data? ANO-MES-DIATHORA:MIN:SEGZ ")
    description = input("Qual a descricao da nota? ")


if endpoint == 1:
    response = requests.get(('http://{0}:80/tasks/tasks/'.format(DNS)))

elif endpoint == 2:
    response = requests.post('http://{0}:80/tasks/tasks/'.format(DNS),
                             data={'title': '{0}'.format(title), 'pub_date': '{0}'.format(date), 'description': '{0}'.format(description)})
else:
    print(id_del)
    response = requests.delete(
        "http://{0}:80/tasks/task/{1}".format(DNS, id_del))

print(response.json())
