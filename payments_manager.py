import os
import inspect
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from statsmodels.tsa.seasonal import seasonal_decompose

# cash_request = pd.read_csv('./data/extract - cash request - data analyst.csv')
# fees = pd.read_csv('../data/extract - fees - data analyst - .csv')

def help():
    print("""Ajuda:
    import payments_manager as bp
    av.Init()
    av.Init("./data/extract - cash request - data analyst.csv","./data/extract - fees - data analyst - .csv")
    av.info()
    av.df("cr") # Cash Request
    av.df("fe") # Fees
    df_sorted = av.sort("cr_date_status", ["Date","region"], asc=[False, True])
    display(av.df("cr_cp"))
    av.add(df,"df_name")
    """)
    
def init(csv_cr="./data/extract - cash request - data analyst.csv", csv_fe ="./data/extract - fees - data analyst - .csv", debug=True):
    Manager(csv_cr, csv_fe)

def df(name):
    return Manager.get_df(name)

def add(df, df_name):
    Manager.add_df(df, df_name)

def sort(dataframe, columns, asc = True):
    return Manager.sort_df(name= dataframe, columns= columns, ascending= asc)

def info():
    Manager.mostrar_info()

def reset():
    Manager.dataframes = {}

#def get_season():
#    return Manager.get_season

def get_map_list(expression, my_list):
    #numbers = [1, 2, 3, 4, 5]
    #cuadrados = list(map(lambda x: x**2, numbers))
    #print(cuadrados)  # [1, 4, 9, 16, 25]
    return list(map(expression, my_list))

class Manager:            
    debug = None
    dataframes = {}

    get_season = lambda date: '1.Primavera' if 3 <= date.month <= 5 else ('2.Verano' if 6 <= date.month <= 8 else ('3.Otoño' if 9 <= date.month <= 11 else '4.Invierno'))

    prop_classification_colors = {'City':'green' ,'Region':'yellow' ,'GreaterRegion':'orange', 'State':'red'}

    @property
    def classification_colors(self):
        return self.prop_classification_colors
    
    @property
    def region_classification(self):
        return self.prop_region_classification

    @classmethod
    def __init__(self, cr_path='./data/extract - cash request - data analyst.csv',
                  fe_path='./data/extract - fees - data analyst - .csv', debug=False):
        """
        Inicializa la clase DatasetLoader.
        
        :param debug: Booleano que indica si se debe mostrar información de depuración.
        :param csv_path: Ruta opcional a un archivo CSV para cargar inmediatamente.
        """
        self.debug = debug
        # Si se proporciona un archivo CSV, se intenta cargarlo
        if cr_path is not None:
            if self.dataframes is not None and len(self.dataframes) >0:
                if debug:
                    print("Debug: Res a fer, les dades ja estan carrgades als datafames.")
            else:    
                self.load_data(cr_path, fe_path)
                self.format_data()

    @classmethod
    def get_df(cls, name='df'):
        """
        Retorna el DataFrame almacenado bajo un nombre específico.
        
        :param name: Nombre del DataFrame a obtener.
        :return: DataFrame correspondiente o None si no existe.
        """
        return cls.dataframes.get(name, None)

    @classmethod
    def add_df(cls, dataframe, name):
        cls.dataframes[name] = dataframe.copy()

    @classmethod
    def sort_df(cls, name, columns, ascending):
        #cls.dataframes[name] = dataframe
        return cls.dataframes.get(name, None).sort_values(columns, ascending= ascending)

    @classmethod
    def load_data(cls, cr_path, fe_path):
        """
        Carga un dataset desde archivos CSV.
        
        :return: None
        """

        if not os.path.exists(cr_path):
            print(f"Error: El archivo '{cr_path}' no existe.")
            return
        if not os.path.exists(fe_path):
            print(f"Error: El archivo '{fe_path}' no existe.")
            return
        try:
            cr = pd.read_csv(cr_path)
            cls.add_df(cr,"cr")
            fe = pd.read_csv(fe_path)
            cls.add_df(fe,"fe")

            if cls.debug:
                print(f"Dataset {cr_path} cargado correctamente.")
                print(f"Dimensiones del dataset cr: {cr.shape}")
                print(f"Columnas: {cr.columns.tolist()}")

                print(f"Dataset {fe_path} cargado correctamente.")
                print(f"Dimensiones del dataset fe: {fe.shape}")
                print(f"Columnas: {fe.columns.tolist()}")
        except Exception as e:
            print(f"Error al cargar el archivo: {e} {e.__traceback__}")
            print(f"line: {e.__traceback__.tb_lineno} tb_frame: {e.__traceback__.tb_frame} ")

    @classmethod
    def format_data(cls):
        """
        Formatea el dataset basado en ...
        
        :param conditions: None
        :return: Un DataFrame con los datos filtrados.
        """
        if cls.get_df("cr") is None:
            print("format_data: El dataset Cash Request no se ha cargado. Usa el método 'load_data' primero.")
            return None
        if cls.get_df("fe") is None:
            print("format_data: El dataset Fees no se ha cargado. Usa el método 'load_data' primero.")
            return None
        
        # Dataframe normalitzat
        cr_cp = cls.get_df("cr").copy()
        fe_cp = cls.get_df("fe").copy()

        cr_cp['created_at'] = pd.to_datetime(cr_cp['created_at']) #Normalizar fechas
        cr_cp['created_at'] = cr_cp['created_at'].dt.tz_localize(None)
        cr_cp['Mes_created_at'] = cr_cp['created_at'].dt.to_period('M')


        # cr_cp = cr_cp.rename(columns={cr_cp.columns[0]: 'Col_0'}) # Primera columna sin titulo, potencialmente eliminable
        # cr_cp = cr_cp.rename(columns={'4046': 'Volume_Hass_S'}) # Etiquetas mas descritivas
        # cr_cp = cr_cp.rename(columns={'4225': 'Volume_Hass_L'})
        # cr_cp = cr_cp.rename(columns={'4770': 'Volume_Hass_XL'})
        # cr_cp = cr_cp.drop('Col_0', axis=1) # Parecen IDs del 0 al 52. Eliminable. 
        # # Col_0 = df_cp['Col_0'].unique()  print(f"Col_0: {Col_0}\n")
        # cr_cp = cr_cp.reset_index()
        
        # # Dataframe normalitzat (df_cp) amb els noms de  columnes simplificats.
        # df_c = cr_cp.rename(columns={"AveragePrice": "av_price", "Total Volume": "to_volume",
        #                               "Volume_Hass_S": "vo_S", "Volume_Hass_L": "vo_L", "Volume_Hass_XL": "vo_XL"})
        # cls.add_df(df_c ,"df_c")

        # df_type = cr_cp.groupby('type')['Total Volume'].count()
        # df_type = df_type.reset_index()
        # cls.add_df(df_type,"df_type")

        # regions = cr_cp['region'].unique() 
        # cls.add_df(regions, "regions")

        # years = cr_cp['year'].unique() 
        # cls.add_df(years, "years")

        # #df_weekly = df_cp.groupby(pd.Grouper(key='Date', freq='W')).count() # ['AveragePrice'].mean()
        # #df_weekly = df_weekly.reset_index()
        # dates = cr_cp['Date'].unique() 
        # cls.add_df(dates, "dates")

        # cr_cp['region_class']= cr_cp['region'].map(cls.prop_region_classification)

        # df_date_price_volume = cr_cp[['Date', 'region', 'AveragePrice', 'Total Volume']]
        # df_date_price_volume = df_date_price_volume.reset_index()
        # df_date_price_volume['Season'] = df_date_price_volume['Date'].apply(cls.get_season)
        # cls.add_df(df_date_price_volume, "df_date_price_volume")

        # # Para seleccionar unicamente las regiones propias , descartamos Total US para la vista gráfica
        # cls.add_df(cr_cp[cr_cp.region != 'TotalUS'],"df_cp_cleaned")

        # cls.add_df(cr_cp[cr_cp['region_class']=='City'],"df_city")
        # cls.add_df(cr_cp[cr_cp['region_class']=='Region'],"df_region")

        # cls.add_df(cr_cp[cr_cp['region_class'].isin(['City','Region'])],"df_city_region")      

        # cls.add_df(cr_cp[cr_cp['region_class']=='GreaterRegion'],"df_greater")
        # cls.add_df(cr_cp[cr_cp['region_class']=='TotalUS'],"df_totalUS")

        # # Las top 10 regions por Total Volume
        # cls.add_df(cr_cp.groupby('region')['Total Volume'].sum().nlargest(10).index,"region_largest")

        # # Exemple
        # df_cp_cleaned=cr_cp[cr_cp.region != 'TotalUS']
        # df_cp_CA=cr_cp[cr_cp.region == 'California']
        # df_cp_noCA=cr_cp[(cr_cp.region != 'TotalUS') & (cr_cp.region != "California")]
        # df_cp_noCA_conventional=cr_cp[(cr_cp.region != 'TotalUS') & (cr_cp.region != "California") & (cr_cp.type=='conventional')]
        # df_cp_noCA_organic=cr_cp[(cr_cp.region != 'TotalUS') & (cr_cp.region != "California") & (cr_cp.type=='organic')]
        # df_cp_organic=cr_cp[(cr_cp.region != 'TotalUS') & (cr_cp.type=='organic')]
        # df_cp_conventional=cr_cp[(cr_cp.region != 'TotalUS') & (cr_cp.type=='conventional')]
        # df_cp_Denver=cr_cp[cr_cp.region == 'Denver']
        # cls.add_df(df_cp_cleaned,"df_cp_cleaned")
        # cls.add_df(df_cp_CA,"df_cp_CA")
        # cls.add_df(df_cp_noCA,"df_cp_noCA")
        # cls.add_df(df_cp_noCA_conventional,"df_cp_noCA_conventional")
        # cls.add_df(df_cp_noCA_organic ,"df_cp_noCA_organic")
        # cls.add_df(df_cp_organic ,"df_cp_organic")
        # cls.add_df(df_cp_conventional ,"df_cp_conventional")
        # cls.add_df(df_cp_Denver ,"df_cp_Denver")

        

        cls.add_df(cr_cp ,"cr_cp")
        cls.add_df(fe_cp ,"fe_cp")
        # TODO
        #cls.add_df(df_jo,"df_jo")        

    @classmethod
    def filter_data(cls, df_name, **conditions):
        """
        Filtra el dataset basado en condiciones especificadas.
        
        :param conditions: Condiciones de filtro en formato clave=valor. 
                           Ejemplo: columna="valor"
        :return: Un DataFrame con los datos filtrados.
        """
        df = cls.get_df(df_name)
        if df is None:
            print("filter_data: El dataset no se ha encontrado.")
            return None
        
        filtered_data = df
        for column, value in conditions.items():
            if column in filtered_data.columns:
                filtered_data = filtered_data[filtered_data[column] == value]
                if cls.debug:
                    print(f"Filtrando por {column}={value}. Dimensiones actuales: {filtered_data.shape}")
            else:
                print(f"Advertencia: La columna '{column}' no existe en el dataset.")
        
        return filtered_data

    @classmethod
    def obtener_regions(cls, filtro):
        return [clave for clave, valor in cls.prop_region_classification.items() if valor == filtro]

    @classmethod
    def mostrar_info(cls):
        """
        Muestra información general del dataset cargado.
        
        :return: None
        """
        
        cr = cls.get_df("cr")
        fe = cls.get_df("fe")
        if cr is None or fe is None:
            print("mostrar_info: Los datasets no se han cargado. Usa el método 'load_data' primero.")
            return

        print(f"Lista de dataframes: {list(cls.dataframes.keys())}")
        if cls.debug:
            print("Información general del dataset:")
            print(cr.info())

            print("Información estadística del dataset:")
            print(cr.describe())

            # years = cls.get_df("years")
            # print(f"\nAños: {years}")

            # regions = cls.get_df("regions")
            # print(f"\nRegiones comerciales: {regions}")

            #print("\nPrimeras 5 filas del dataset df_cp:")
            #df_cp = cls.get_df("df_cp")
            #print(df_cp.head())

#region_classification = Manager.prop_region_classification
classification_colors = Manager.prop_classification_colors

color_orga ='green'; color_conv ='grey'; color_total ='blue'