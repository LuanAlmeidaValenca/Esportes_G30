import plotly.graph_objects as go

def create_radar_chart(data_series, attributes, title="Desempenho", max_score=10):
    """
    Cria um gráfico de radar interativo.
    
    :param data_series: Lista de dicionários, ex: [{'name': 'Joao', 'scores': [8, 7, 9]}, ...]
    :param attributes: Lista de strings com os nomes dos atributos, ex: ['Passe', 'Chute', 'Fisico']
    :param title: Título do gráfico.
    :param max_score: Valor máximo do eixo (geralmente 10 ou 100).
    :return: Objeto figura do Plotly.
    """
    fig = go.Figure()

    # Para fechar o polígono do gráfico de radar, precisamos repetir o primeiro elemento no final
    closed_attributes = attributes + [attributes[0]]

    for series in data_series:
        name = series.get("name", "Jogador")
        scores = series.get("scores", [])
        
        # Repete a primeira nota no final para fechar o desenho no gráfico
        closed_scores = scores + [scores[0]]

        fig.add_trace(go.Scatterpolar(
            r=closed_scores,
            theta=closed_attributes,
            fill='toself',
            name=name
        ))

    fig.update_layout(
        title=title,
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, max_score]
            )
        ),
        showlegend=True,
        margin=dict(l=50, r=50, t=50, b=50)
    )

    return fig