# SeeR Model Zoo Web App

This is a web application to showcase the results of different anomaly detection models running on different datasets. The app is designed to automatically enable "plug and play" of different models on different datasets. 

To add a model, add the `.pkl` file for the model (generated using `model.save`) to the `models/` directory. Name the model something informative using Python function naming conventions, because the web app will automatically pretty print the name given (e.g. "isolation_forest_contextual.pkl" will be pretty-printed as "Isolation Forest Contextual". The model must reference a valid featurizer (`model.featurizer`). Note that this featurizer is not actually contained within the `.pkl` file, which only contains a reference to the function in other code. Then the featurizer corresponding to a model must be kept in place even after new models have been built. 

To add a dataset, wrap it in the `Test_data` class, pickle it using the pickle module and `pickle.dump`, and then add it to the `datasets/` directory, following the same naming convention mentioned above.