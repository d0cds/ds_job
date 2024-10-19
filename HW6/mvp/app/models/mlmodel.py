from catboost import CatBoostRegressor
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize, MinMaxScaler, OneHotEncoder
from sklearn.decomposition import PCA
import json
from models.data import Data, Dataloc


# Класс ML модели по предсказанию уровня зп в зависимости от комбинации скиллов
class MLModel():
    def predict(data: json) -> str:
        model = CatBoostRegressor()
        model.load_model('./catboost', format="cbm")
        # получаем DataFrame из таблицы с данными
        df = Data.get_data_all()
        data_loc = Dataloc.get_data_all()
        # преобразуем данные
        # создаем кодер для колонки type_busy
        ohe_encoded_type_busy = OneHotEncoder(sparse_output = False)
        encoded_type_busy = ohe_encoded_type_busy.fit(df[["type_busy"]])
        # создаем кодер для колонки qualification
        ohe_encoded_qualification = OneHotEncoder(sparse_output = False)
        encoded_qualification = ohe_encoded_qualification.fit(df[["qualification"]])
        # создаем кодер для колонки federalDistrictCode
        ohe_encoded_federalDistrictCode = OneHotEncoder(sparse_output = False)
        encoded_federalDistrictCode = ohe_encoded_federalDistrictCode.fit(df[["federalDistrictCode"]])
        # создаем кодер для колонки skills
        tfidf_vectorizer_skills = TfidfVectorizer(ngram_range = (1,2), stop_words = "english")
        tfidf_matrix_skills = tfidf_vectorizer_skills.fit_transform(df["skills"].str.lower().tolist())
        tfidf_matrix_skills_normalized = normalize(tfidf_matrix_skills , norm='l2', axis=1)
        Tfidf_df = pd.DataFrame(tfidf_matrix_skills_normalized.toarray(), columns =tfidf_vectorizer_skills.get_feature_names_out())
        # создаем кодер PCA для колонки skills
        pca = PCA(n_components = 150)
        pca_skills = pca.fit_transform(Tfidf_df)
        
        sc = MinMaxScaler()
        df["salary_stat_mean_1"] = (df["salary_stat_mean"].mean()/df["salary_stat_mean"])
        df["salary_stat_mean_2"] = (df["salary_stat_mean"]/df["salary_stat_mean"].max())
        df["salary_stat_mean_3"] = (df["salary_stat_mean"]/df["salary_stat_mean"].min())
        df["salary_stat_mean_4"] = (df["salary_stat_mean"].median()/df["salary_stat_mean"])
        #перемножение, требует нормализации
        df["salary_stat_mean_6"] = (df["salary_stat_mean"].mean()*df["salary_stat_mean"])
        df["salary_stat_mean_7"] = (df["salary_stat_mean"]*df["salary_stat_mean"].max())
        df["salary_stat_mean_8"] = (df["salary_stat_mean"]*df["salary_stat_mean"].min())
        df["salary_stat_mean_9"] = (df["salary_stat_mean"].median()*df["salary_stat_mean"])
        salary_sc = sc.fit_transform(df[['salary_stat_mean', 'salary_stat_mean_1',
                                        'salary_stat_mean_2', 'salary_stat_mean_3', 'salary_stat_mean_4',
                                        'salary_stat_mean_6', 'salary_stat_mean_7',
                                        'salary_stat_mean_8', 'salary_stat_mean_9']])

        data = {k:v.lower() for k,v in data.items()}
        d_js_tfidf_matrix_skills = normalize(tfidf_vectorizer_skills.transform([data["skills"].lower().strip()]) , norm='l2', axis=1).toarray()
        data_skills_tfIdf = pd.DataFrame(d_js_tfidf_matrix_skills, columns =tfidf_vectorizer_skills.get_feature_names_out())
        
        data_PCA = pd.DataFrame(pca.transform(data_skills_tfIdf), columns=[f'PCA_{i+1}' for i in range(150)])

        data_df_type_busy = pd.DataFrame(encoded_type_busy.transform([[data["type_busy"]]]),columns = encoded_type_busy.get_feature_names_out(), dtype=int)
        data_df_type_busy.drop("type_busy_internship", inplace=True, axis=1)
        data_df_qualification = pd.DataFrame(encoded_qualification.transform([[data["qualification"]]]),columns = encoded_qualification.get_feature_names_out(), dtype=int)
        data_df_qualification.drop("qualification_Not_qualification", inplace=True, axis=1)
        if data["location"] not in df["location"]:
            val = "Not_location"
        else:
            val = data["location"]
        data_df_federalDistrictCode = pd.DataFrame(encoded_federalDistrictCode.transform([data_loc.cod[data_loc.location==val].values]),columns = encoded_federalDistrictCode.get_feature_names_out(), dtype=int)
        data_df_federalDistrictCode.drop("federalDistrictCode_Not_cod", inplace=True, axis=1)
        if data["location"] not in df["location"]:
            salary_stat_mean = data_loc.salary[data_loc.location==val]
        else:
            salary_stat_mean = df.salary_stat_mean[df.locatio==data["location"]]
        data_salary = pd.DataFrame.from_dict({'salary_stat_mean': [salary_stat_mean], 
                                        'salary_stat_mean_1':[(df['salary_stat_mean'].mean()/salary_stat_mean)],
                                            'salary_stat_mean_2': [salary_stat_mean/df['salary_stat_mean'].max()],
                                            'salary_stat_mean_3':[salary_stat_mean/df['salary_stat_mean'].min()],
                                            'salary_stat_mean_4': [df['salary_stat_mean'].median()/salary_stat_mean],
                                            'salary_stat_mean_6':[df['salary_stat_mean'].mean()*salary_stat_mean],
                                            'salary_stat_mean_7': [salary_stat_mean*df['salary_stat_mean'].max()],
                                            'salary_stat_mean_8':[salary_stat_mean*df['salary_stat_mean'].min()],
                                            'salary_stat_mean_9': [df['salary_stat_mean'].median()*salary_stat_mean]
                                            })

        data_pred = pd.concat([pd.DataFrame.from_dict({"name_job":[data['name_job']], "location":[data['location']]}),
                                pd.DataFrame(sc.transform(data_salary), columns=data_salary.columns), 
                                data_df_type_busy,
                                data_df_qualification,
                                data_df_federalDistrictCode, 
                                data_PCA],axis=1)
        
        result = np.exp(model.predict(data_pred))
        
        return str(round(result[0], -3))