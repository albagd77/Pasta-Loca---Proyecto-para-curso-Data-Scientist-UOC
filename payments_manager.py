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
        return cls.dataframes.get(name, None).copy()

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
        
        # Normalitzar i deslocalitzar dates
        date_cols = ['updated_at','moderated_at','reimbursement_date','cash_request_received_date',
                    'money_back_date','send_at','reco_creation','reco_last_update']
        for col in date_cols:
            if col in cr_cp.columns:  # Comprova si la columna existeix
                # cr_cp[col] = pd.to_datetime(cr_cp[col], errors='coerce')  # Normalitza les dates ## !! aixo descarta dates !!
                cr_cp[col] = pd.to_datetime(cr_cp[col],format='ISO8601')
                cr_cp[col] = cr_cp[col].dt.tz_localize(None)  # Elimina la informació de zona horària
        cr_cp['user_id'] = cr_cp['user_id'].fillna(0).astype(int)
        #cr_cp.info()
        #display(cr_cp)

        #if 'cash_request_id' not in fe_cp.columns:
        #    fe_cp['cash_request_id'] = 0  # O un altre valor predeterminat
        fe_cp['cash_request_id'] = fe_cp['cash_request_id'].fillna(0).astype(int)
        #fe_cp['cash_request_id'] = fe_cp['cash_request_id'].astype(int)

        # Normalitzar i deslocalitzar dates
        date_cols = ['created_at','updated_at','paid_at','from_date','to_date']
        for col in date_cols:
            if col in fe_cp.columns:  # Comprova si la columna existeix
                #fe_cp[col] = pd.to_datetime(fe_cp[col], errors='coerce')  # Normalitza les dates
                fe_cp[col] = pd.to_datetime(fe_cp[col],format='ISO8601')
                fe_cp[col] = fe_cp[col].dt.tz_localize(None)  # Elimina la informació de zona horària
        #fe_cp.info()

        # Verifica duplicats a fe_cp
        #duplicats_fe_cp = fe_cp[fe_cp.duplicated(subset=['id', 'cash_request_id'], keep=False)]
        #print(duplicats_fe_cp)

        # Verifica duplicats a cr_cp
        #duplicats_cr_cp = cr_cp[cr_cp.duplicated(subset=['id'], keep=False)]
        #print(duplicats_cr_cp)

        #display(fe_cp[['id','cash_request_id']])
        #df_jo = pd.merge(cr_cp, fe_cp,  on=['id','cash_request_id'], how ="left")
        df_jo = pd.merge(cr_cp, fe_cp, left_on='id', right_on='cash_request_id', how ="left") #inner
    
        #df_jo.info()

        #pm.add(df_jo,"df_jo")

        # Añadir la columna 'active': 1 si deleted_account_id es NaN, de lo contrario 0
        df_jo['active'] = df_jo['deleted_account_id'].apply(lambda x: 1 if pd.isna(x) else 0)

        # Migrar user_id:
        # - Para las filas donde deleted_account_id existe, usar "99" + deleted_account_id
        # - De lo contrario, mantener el user_id original
        df_jo['user_id'] = df_jo.apply(
            lambda row: int(f"{99000000+int(row['deleted_account_id'])}") if not pd.isna(row['deleted_account_id']) else row['user_id'],
            axis=1
        )
        # Eliminar la columna 'deleted_account_id'
        df_jo = df_jo.drop(columns=['deleted_account_id'])

        df_jo.insert(df_jo.columns.get_loc("user_id")+1,"active",df_jo.pop("active"))

        # fields_actions = ['id_x as id_cr','amount','status_x as stat_cr','created_at_x','user_id','moderated_at: 0=manual 1=auto',
        #           'reimbursement_date','cash_request_received_date', 'money_back_date','transfer_type','send_at',
        #           'recovery_status: 0= null, 1=no, 2=si, etc.','','type','status_y as stat_fe','category','total_amount','paid_at',
        #           'from_date','to_date','charge_moment 0=after, 1=before']

        # Renombrar
        df_jo = df_jo.rename(columns={'id_x': 'id_cr'})
        df_jo = df_jo.rename(columns={'id_y': 'id_fe'})
        df_jo = df_jo.rename(columns={'status_x': 'stat_cr'})
        df_jo = df_jo.rename(columns={'created_at_x': 'created_at'})
        df_jo = df_jo.rename(columns={'created_at_y': 'created_at_fe'})
        df_jo = df_jo.rename(columns={'status_y': 'stat_fe'})
        
        df_jo['id_fe'] = df_jo['id_fe'].fillna(0).astype(int)

        # Copiar para mantener compatibilidad
        #df_jall = df_jall.rename(columns={'cash_request_received_date': 'cr_received_date'})
        df_jo['cr_received_date'] = df_jo['cash_request_received_date']

        #df_jo['fee'] = df_jo['total_amount']
        df_jo = df_jo.rename(columns={'total_amount': 'fee'})
        
        df_jo['Mes_created_at'] = df_jo['created_at'].dt.to_period('M')
        

        # Tiempo que tarda en recibir el dinero el usuario desde la primera accion.
        # cr_received_date  (cash_request_received_date) = ??
        df_jo['to_receive_ini'] = df_jo.cash_request_received_date-df_jo.created_at

        # Tiempo que tarda en recibir el dinero el usuario desde que se envia (demora entre bancos).
        df_jo['to_receive_bank'] = df_jo.cash_request_received_date-df_jo.send_at

        # Tiempo que la empresa recupera el dinero desde la primera accion.
        df_jo['to_reimbur'] = df_jo.reimbursement_date-df_jo.created_at

        # Tiempo en el que la emprera realmente ha prestado el dinero
        df_jo['to_reimbur_cash'] = df_jo.reimbursement_date-df_jo.send_at

        # Tiempo que la empresa presta el dinero.
        df_jo['to_end'] = df_jo.reimbursement_date-df_jo.money_back_date

        #* Demora:
        #df['to_delay'] = df_jo.money_back_date-df_jo.reimbursement_date

        # En funcion del tipo instant o regular:
        # TransfType: instant send_at - created_at =? 0 dias
        # TransfType: regular send_at - created_at =? 7 dias
        df_jo['to_send'] = df_jo.send_at-df_jo.created_at


        df_jall = df_jo.copy()
        
        

        # Eliminar
        df_jo = df_jo.drop(columns=['updated_at_x'])
        #df_jo = df_jo.drop(columns=['recovery_status'])
        df_jo = df_jo.drop(columns=['reco_creation'])
        df_jo = df_jo.drop(columns=['reco_last_update'])
        #df_jo = df_jo.drop(columns=['id_y'])
        df_jo = df_jo.drop(columns=['cash_request_id'])
        #df_jo = df_jo.drop(columns=['reason'])
        #df_jo = df_jo.drop(columns=['created_at_y'])
        df_jo = df_jo.drop(columns=['updated_at_y'])

        '''
            id_x                        32094 non-null  int64         
        1   amount                      32094 non-null  float64       
        2   status_x                    32094 non-null  object        
        3   created_at_x                32094 non-null  datetime64[ns]
        4   updated_at_x                32094 non-null  datetime64[ns]
        5   user_id                     32094 non-null  int64         
        (pasar de qualitativo a quant.) 6   moderated_at                21530 non-null  datetime64[ns]
        7   deleted_account_id          2573 non-null   float64       
        8   reimbursement_date          4061 non-null   datetime64[ns]
        9   cash_request_received_date  24149 non-null  datetime64[ns]
        10  money_back_date             17204 non-null  datetime64[ns]
        11  transfer_type               32094 non-null  object        
        12  send_at                     22370 non-null  datetime64[ns]
        
        13  recovery_status             7200 non-null   object        
        14  reco_creation               7200 non-null   datetime64[ns]
        15  reco_last_update            7200 non-null   datetime64[ns]
        
        16  (Mes_created_at) calculada  32094 non-null  period[M]     
        17  id_y                        21057 non-null  float64       
        18  cash_request_id             21057 non-null  float64       
        19  type                        21057 non-null  object        
        20  status_y                    21057 non-null  object        
        21  category                    2196 non-null   object        
        22  total_amount                21057 non-null  float64       
        23  reason                      21057 non-null  object        
        24  created_at_y                21057 non-null  datetime64[ns]
        25  updated_at_y                21057 non-null  datetime64[ns]
        26  paid_at                     15438 non-null  datetime64[ns]
        27  from_date                   6749 non-null   datetime64[ns]
        28  to_date                     6512 non-null   datetime64[ns]
        29  charge_moment   
        '''
        cls.add_df(cr_cp ,"cr_cp")
        cls.add_df(fe_cp ,"fe_cp")        
        cls.add_df(df_jo,"df_jo")
        cls.add_df(df_jall,"df_jall")
        #print(df_jo.info())        

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