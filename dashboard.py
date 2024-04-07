import pandas as pd
import plotly.express as px
import streamlit as st
import altair as alt
import plotly.graph_objects as go
import math
import numpy as np

st.set_page_config(layout='wide')

#
#  carregando dados
df = pd.read_excel('projetoPy.xlsx')

#
#  medias 
media = df['NPS'].mean()     # media 31.768368055555555
mediana = df['NPS'].median() # mediana 32.1
moda = df['NPS'].mode()[0]   # moda 34.7

#
#  tratando dos dias 
df_filtered = df.copy()
df_filtered['day'] = df_filtered['Período de início'].apply(lambda x: str(x.month) + "-" + str(x.day))
day = st.sidebar.selectbox('Dia', df_filtered['day'].unique() )

df_filtered_day = df_filtered[df_filtered['day'] == day]

#
#  valores maximo e minino 
valores_min = df['NPS'].min()
valores_max = df['NPS'].max()

df_filtered['maxima'] = valores_max 
df_filtered['minima'] = valores_min

data = {'Tipo': ['Maxima', 'Minima'], 'Valor': [valores_max, valores_min]}
df_nps_maximo = pd.DataFrame(data)


# Número de classes usando a regra de Sturges 
num_classes = math.ceil(1 + math.log2(len(df))) # 15

#  A amplitude amostral 
amplitude_amostral = valores_max - valores_min # 51.8



# amplitude de cada classe 
amplitude_classe = amplitude_amostral / num_classes
# amplitude_classe = (valores_max - valores_min) / num_classes


#  limites_classes 
limites_classes = [(valores_min + i * amplitude_classe, valores_min + (i+1) * amplitude_classe) for i in range(num_classes)]

# Pontos Médios das Classes
pontos_medios = [(limite[0] + limite[1]) / 2 for limite in limites_classes]

# Calcular a contagem de valores para cada classe
contagens_classes = []
for limite in limites_classes:
    contagem = ((df['NPS'] >= limite[0]) & (df['NPS'] < limite[1])).sum()
    contagens_classes.append(contagem)

# Criar DataFrame com os limites de classe e as contagens
df_classes = pd.DataFrame({'Classe': range(1, num_classes+1),
                           'Limite Inferior': [limite[0] for limite in limites_classes],
                           'Limite Superior': [limite[1] for limite in limites_classes],
                           'Contagem': contagens_classes})


# Calcula a frequência de cada valor de NPS
frequencia_por_nps = df['NPS'].value_counts().sort_index()

# Calcula o total de observações
total_observacoes = frequencia_por_nps.sum()

# Calcula a frequência relativa de cada valor de NPS
frequencia_relativa_por_nps = frequencia_por_nps / total_observacoes

# Calcula a frequência relativa em percentagem
frequencia_relativa_percentual_por_nps = (frequencia_relativa_por_nps * 100).round(2)


# Calcula a frequência acumulada
frequencia_acumulada = frequencia_por_nps.cumsum()

df_frequencias = pd.DataFrame({
    'NPS': frequencia_por_nps.index,
    'F': frequencia_por_nps.values,
    'FR': frequencia_relativa_por_nps.values,
    'FR(%)': frequencia_relativa_percentual_por_nps.values,
    'FA': frequencia_acumulada.values

})

df_limites_classes = pd.DataFrame(limites_classes, columns=['Limite Inferior', 'Limite Superior'])
df_limites_classes = df_limites_classes.round(2)
df_limites_classes['Ponto Médio'] = pd.Series(pontos_medios).round(2)




############################### Montando tela #############


# Adicionando elementos à barra lateral
st.sidebar.header("Dados")

# Mostra a tabela com as colunas 'Hora' e 'NPS' na barra lateral

# Criando as colunas na interface do Streamlit
col1_top, col2_top = st.columns(2)
col2_1top, col2_2top = col2_top.columns(2)
col1_bottom, col2_bottom,col3_bottom = st.columns(3)


st.sidebar.dataframe(df_filtered_day[['Período de início', 'NPS']])


# # Criando o gráfico de linhas com Plotly Express


#
#################################  FIGURA DADOS GERAIS  ############################################
fig_date = px.line(df_filtered_day, 
    y='NPS', 
    x='Período de início',  
    title='NÍVEIS DE PRESSÃO SONORA' ,
    labels={
        'NPS': 'Nps',
        'Período de início': 'Horário'
    },
    template='plotly_white',
    
)


fig_date.add_shape( # add a horizontal "target" line
    type="line", line_color="red", line_width=2, opacity=1, line_dash="solid",
    x0=0, x1=1, xref="paper", y0=mediana, y1=mediana, yref="y",name="Mediana",
)
fig_date.add_shape( # add a horizontal "target" line
    type="line", line_color="green", line_width=3, opacity=1, line_dash="solid",
    x0=0, x1=1, xref="paper", y0=media, y1=media, yref="y",name="Média", 
)

fig_date.add_shape( # add a horizontal "target" line
    type="line", line_color="yellow", line_width=2, opacity=1, line_dash="solid",
    x0=0, x1=1, xref="paper", y0=moda, y1=moda, yref="y",name="Moda",
)
fig_date.update_traces(textposition="bottom right")
col1_top.plotly_chart(fig_date, use_container_width=True)

#
#################################  FIGURA VALORES MAXIMOS E MINIMOS ############################################
fig_maxima = px.bar(
    df_nps_maximo, 
    x='Tipo', 
    y='Valor',
    color="Tipo",
    title='NPS MAXIMO E MINIMO',

)
fig_maxima.update_layout(legend_title_text='Legenda')
col2_2top.plotly_chart(fig_maxima, use_container_width=True)

#
#################################  FIGURA MEDIAS ############################################
fig_medias = px.pie(names=['Média', 'Mediana', 'Moda'], values=[media, mediana, moda], title='MEDIA MEDIANA MODA')
col2_1top.plotly_chart(fig_medias, use_container_width=True)


#
#################################  FIGURA CLASSES ############################################
fig_classes = px.bar(df_classes, x='Classe', y='Contagem', 
                      hover_data=['Limite Inferior', 'Limite Superior'],
                      labels={'Contagem': 'Contagem de Valores', 'Classe': 'Classe'},
                      title='DISTRIBUIÇÃO DOS VALORES DE NPS EM CLASSE',
                      color_discrete_sequence=['blue'],  # Cor das barras
                      template='plotly_white')  # Estilo do gráfico
col1_bottom.plotly_chart(fig_classes, use_container_width=True)





# Mostra o frequecias na col2_bottom
# col2_bottom.write(df_frequencias, use_container_width=True)
col2_bottom.markdown("### FREQUÊNCIAS")
col2_bottom.write(df_frequencias, use_container_width=True, align="center")

col3_bottom.markdown("### LIMITES E PONTO MEDIO")
col3_bottom.write(df_limites_classes, use_container_width=True, align="center")


st.sidebar.write(f"Amplitude Amostral: {amplitude_amostral}")
st.sidebar.write(f"Amplitude Classes: {amplitude_classe:.2f}")


