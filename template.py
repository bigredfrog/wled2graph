template = """
{% block head %}
<style>
    body {
        background-color: #333;
        color: #fff;
        font-family: 'Arial', sans-serif;
    }
    h1 {
        font-size: 24px;
    }
    table {
        width: 100%;
        border-collapse: collapse;
    }
    th, td {
        border: 1px solid #fff;
        padding: 8px;
        color: #fff;
    }
    th {
        background-color: #555;
    }
</style>
{{ super() }}
{% endblock %}
"""
