import pandas as pd
import requests

# Ruta del archivo CSV
csv_file = "filtrado_pedidos.csv"

# URL de la API
api_url = "https://money.quhou123.com/Api/addCashbookTransaction"

# Token de autenticación (reemplázalo con tu token real)
token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiIsImlzcyI6ImFkbWluLnF1aG91MTIzLmNvbSJ9.eyJpc3MiOiJhZG1pbi5xdWhvdTEyMy5jb20iLCJhdWQiOiJtb25leS5xdWhvdTEyMy5jb20iLCJqdGkiOiIxNDk0NjkzIiwiaWF0IjoiMTc0Mjk0MTQ4OS42MDkxODEiLCJuYmYiOiIxNzQyOTQxNTQ5LjYwOTE4MSIsImV4cCI6IjE3NDI5NDUwODkuNjA5MTgxIiwiZGF0YSI6eyJ1c2VyX2lkIjoiMTQ5NDY5MyIsInR5cGUiOiJhcGlfY2xpZW50IiwiY3JlYXRlZF9hdCI6MTc0Mjk0MTQ4OX19.7O6Zz8IQoOWpz6Y5ZBpOrcC-ZVWAug8YlwWVZ2MJUes"

# ID del cashbook (reemplázalo con el ID real)
cashbook_id = "4359"

# ID de la categoría (reemplázalo con la categoría correcta)
category_id = "7c0b90af-d3cd-402d-893c-acb51edd716b"

# Encabezados
headers = {
    "Content-Type": "application/x-www-form-urlencoded"
}

# Leer el archivo CSV
df = pd.read_csv(csv_file)

# Iterar sobre las filas del CSV y enviar los datos a la API
for index, row in df.iterrows():
    try:
        amount = float(row["Ingresos Netos"].replace("$", "").replace(",", ""))
        payload = {
            "token": token,
            "cashbook_id": cashbook_id,
            "type": 1,  # 1 para ingresos
            "amount": amount,
            "category_id": category_id,
            "remark": f"Pedido {row['Pedido']}",
            "date": row["Fecha"]
        }
        
        response = requests.post(api_url, data=payload, headers=headers)  # Cambio a data en lugar de json
        
        print(f"Enviando: {payload}")
        print(f"Respuesta: {response.status_code} - {response.text}")
        
        if response.status_code == 200:
            print(f"Pedido {row['Pedido']} insertado correctamente.")
        else:
            print(f"Error al insertar pedido {row['Pedido']}: {response.text}")
    except Exception as e:
        print(f"Error procesando pedido {row['Pedido']}: {str(e)}")
