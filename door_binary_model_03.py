# -*- coding: utf-8 -*-
"""glassdoor_model_03.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1JK49as97xG1fEu6mh_4-X3YATvhQPDjL

## Part 3: Preliminary prediction modeling

*   Built Logistic Regression (LR) and Random Forest (RF) models for predicting apply or not-apply.
*   Found AUC on test dateset from LR and RF are only slightly higher than 0.5, the probability when randomly predict. 
*   Recall and precision approach to zeros from these models, suggesting their prediction results are inaccurate.
"""

from google.colab import drive
drive.mount('/content/gdrive')

# Commented out IPython magic to ensure Python compatibility.
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
# %matplotlib inline
plt.style.use('ggplot')

import warnings
warnings.filterwarnings('ignore')

# read data that treat missing value and log transformation


df = pd.read_csv('/content/gdrive/My Drive/Colab Notebooks/glassdoor/Apply_Rate_2019_cleaned_log.csv')

df.head()

df = df.drop(['class_id', 'Is_apply', 'city_match'], axis=1)

a = pd.get_dummies(df['Is_city_match'], columns = ['city_match_binary'])
df = df.drop(['Is_city_match'], axis=1)
df_model = df.join(a)

print(df_model.columns)

print('\nthe size of data frame for modeling is: ', df_model.shape)

df_model.search_date.value_counts()

df_model.head()

# split train and test dataset by 'search_date'

test_date = df_model['search_date'] == '01-27'
df_test = df_model[test_date]

train_date = df_model['search_date'] != '01-27'
df_train = df_model[train_date]


print('size of train set: ' , df_train.shape)
print('size of test set: ' , df_test.shape)

y_train = df_train['apply']
X_train = df_train.drop(['apply', 'search_date'], axis=1)

y_test = df_test['apply']
X_test = df_test.drop(['apply', 'search_date'], axis=1)

# pre-process data before modeling

from sklearn import preprocessing
b

def train_test_model(clf, X_train, y_train, X_test, y_test):
    clf.fit(X_train, y_train)
    y_train_pred = clf.predict(X_train)
    p_train_pred = clf.predict_proba(X_train)[:,1]

    y_test_pred = clf.predict(X_test)
    p_test_pred = clf.predict_proba(X_test)[:,1]

    get_performance_metrics(y_train, p_train_pred, y_test, p_test_pred)
    plot_roc_curve(y_train, p_train_pred, y_test, p_test_pred)

from sklearn.metrics import roc_curve, auc

def plot_roc_curve(y_train, y_train_pred, y_test, y_test_pred):
    roc_auc_train = roc_auc_score(y_train, y_train_pred)
    fpr_train, tpr_train, _ = roc_curve(y_train, y_train_pred)

    roc_auc_test = roc_auc_score(y_test, y_test_pred)
    fpr_test, tpr_test, _ = roc_curve(y_test, y_test_pred)
    plt.figure()
    lw = 2
    plt.plot(fpr_train, tpr_train, color='green',
             lw=lw, label='ROC Train (AUC = %0.4f)' % roc_auc_train)
    plt.plot(fpr_test, tpr_test, color='darkorange',
             lw=lw, label='ROC Test (AUC = %0.4f)' % roc_auc_test)
    plt.plot([0, 1], [0, 1], color='navy', lw=lw, linestyle='--')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('Receiver operating characteristic example')
    plt.legend(loc="lower right")
    plt.show()

from sklearn.metrics import precision_score, accuracy_score, recall_score, f1_score, roc_auc_score

def get_performance_metrics(y_train, y_train_pred, y_test, y_test_pred, threshold=0.5):
    metric_names = ['AUC','Accuracy','Precision','Recall','f1-score']
    metric_values_train = [roc_auc_score(y_train, y_train_pred),
                    accuracy_score(y_train, y_train_pred>threshold),
                    precision_score(y_train, y_train_pred>threshold),
                    recall_score(y_train, y_train_pred>threshold),
                    f1_score(y_train, y_train_pred>threshold)
                   ]
    metric_values_test = [roc_auc_score(y_test, y_test_pred),
                    accuracy_score(y_test, y_test_pred>threshold),
                    precision_score(y_test, y_test_pred>threshold),
                    recall_score(y_test, y_test_pred>threshold),
                    f1_score(y_test, y_test_pred>threshold)
                   ]
    all_metrics = pd.DataFrame({'metrics':metric_names,
                                'train':metric_values_train,
                                'test':metric_values_test},columns=['metrics','train','test']).set_index('metrics')
    print(all_metrics)

"""*Logistic regression*"""

from sklearn.linear_model import LogisticRegressionCV
clf = LogisticRegressionCV(cv=5, solver='lbfgs', penalty='l2',random_state=0)
clf.fit(X_train, y_train)
train_test_model(clf, X_train, y_train, X_test, y_test)

"""*Random Forest*"""

from sklearn.ensemble import RandomForestClassifier
parameters = {'n_estimators': 50,
              'max_features': 'auto',
              'criterion': 'gini',
              'max_depth': 20,
              'min_samples_split': 2,
              'min_samples_leaf': 20,
              'random_state': 0,
              'n_jobs': -1
              }

clf = RandomForestClassifier(**parameters)
clf.fit(X_train, y_train)
train_test_model(clf, X_train, y_train, X_test, y_test)

"""Conclusions:
1. Logistic regression and Random Forest showed that AUC on test is sligtly higher than 0.5, the probability when randomly predict apply_rate.

2. Both models produced precision and recall with zero values, which suggest that these models produce inaccurate prediction results. 



---
"""





"""## Part 4: Modeling with multiple sampling methods

*   I hypothesized that misleading prediction results from above part was due to imbalanced distribution of label, which 'apply' takes less than 9% of population.
*   Perform re-sampling via three methods, up-sampling, down-sampling and synthetic minority oversampling techniques (SMOTE).
"""

df.head()

# split train and test dataset by 'search_date'

test_date = df_model['search_date'] == '01-27'
df_test = df_model[test_date]

train_date = df_model['search_date'] != '01-27'
df_train = df_model[train_date]

y_train = df_train['apply']
X_train = df_train.drop(['apply', 'search_date'], axis=1)

y_test = df_test['apply']
X_test = df_test.drop(['apply', 'search_date'], axis=1)



"""*4.1. Up-sample from minority of 'apply' *"""

#1a. concatenate our training data back together
X = pd.concat([X_train, y_train], axis=1)

#1b. separate minority and majority classes
not_apply = X[X['apply'] == 0]
apply = X[X['apply'] == 1]

#1c. upsample minority
from sklearn.utils import resample
apply_upsampled = resample(apply,
                          replace=True, # sample with replacement
                          n_samples=len(not_apply), # match number in majority class
                          random_state=0) # reproducible results

#1d. combine majority and upsampled minority
df_upsampling = pd.concat([not_apply, apply_upsampled])

df_upsampling['apply'].value_counts()

y_train_up = df_upsampling['apply']
X_train_up = df_upsampling.drop(['apply'], axis=1)

X_train_up  = preprocessing.scale(X_train_up )
X_test  = preprocessing.scale(X_test)

"""*Logistic Regression*"""

from sklearn.linear_model import LogisticRegressionCV
clf = LogisticRegressionCV(cv=5, solver='lbfgs', penalty='l2',random_state=0)
clf.fit(X_train, y_train)
train_test_model(clf, X_train_up, y_train_up, X_test, y_test)

"""*Random Forest*"""

from sklearn.ensemble import RandomForestClassifier
parameters = {'n_estimators': 50,
              'max_features': 'auto',
              'criterion': 'gini',
              'max_depth': 20,
              'min_samples_split': 2,
              'min_samples_leaf': 20,
              'random_state': 0,
              'n_jobs': -1
              }

clf = RandomForestClassifier(**parameters)
clf.fit(X_train, y_train)
train_test_model(clf, X_train_up, y_train_up, X_test, y_test)



"""*4.2. Down-sample from majority of 'not_apply' *"""

#1a. concatenate our training data back together
X = pd.concat([X_train, y_train], axis=1)


#1b. separate minority and majority classes
not_apply = X[X['apply'] == 0]
apply = X[X['apply'] == 1]


#1c. upsample minority
from sklearn.utils import resample
notapply_dwsampled = resample(not_apply,
                          replace=True, # sample with replacement
                          n_samples=len(apply), # match number in majority class
                          random_state=0) # reproducible results

#1d. combine majority and upsampled minority
df_dwsampling = pd.concat([apply, notapply_dwsampled])

df_dwsampling['apply'].value_counts()

y_train_dw = df_upsampling['apply']
X_train_dw = df_upsampling.drop(['apply'], axis=1)

X_train_dw  = preprocessing.scale(X_train_dw )
X_test  = preprocessing.scale(X_test)

"""*Logistic Regression*"""

from sklearn.linear_model import LogisticRegressionCV
clf = LogisticRegressionCV(cv=5, solver='lbfgs', penalty='l2',random_state=0)
clf.fit(X_train, y_train)
train_test_model(clf, X_train_dw, y_train_dw, X_test, y_test)

"""*Random Forest*"""

from sklearn.ensemble import RandomForestClassifier
parameters = {'n_estimators': 50,
              'max_features': 'auto',
              'criterion': 'gini',
              'max_depth': 20,
              'min_samples_split': 2,
              'min_samples_leaf': 20,
              'random_state': 0,
              'n_jobs': -1
              }

clf = RandomForestClassifier(**parameters)
clf.fit(X_train, y_train)
train_test_model(clf, X_train_dw, y_train_dw, X_test, y_test)

"""*4.3. SMOTE on minority 'apply' *"""

from imblearn.over_sampling import SMOTE


sm = SMOTE(random_state=0, ratio=1.0)
X_train_sm, y_train_sm = sm.fit_sample(X_train, y_train)

X_train_sm  = preprocessing.scale(X_train_sm )
X_test  = preprocessing.scale(X_test)

"""*Logistic Regression*"""

from sklearn.linear_model import LogisticRegressionCV
clf = LogisticRegressionCV(cv=5, solver='lbfgs', penalty='l2',random_state=0)
clf.fit(X_train, y_train)
train_test_model(clf, X_train_sm, y_train_sm, X_test, y_test)

"""*Random Forest*"""

from sklearn.ensemble import RandomForestClassifier
parameters = {'n_estimators': 50,
              'max_features': 'auto',
              'criterion': 'gini',
              'max_depth': 20,
              'min_samples_split': 2,
              'min_samples_leaf': 20,
              'random_state': 0,
              'n_jobs': -1
              }

clf = RandomForestClassifier(**parameters)
clf.fit(X_train, y_train)
train_test_model(clf, X_train_sm, y_train_sm, X_test, y_test)



