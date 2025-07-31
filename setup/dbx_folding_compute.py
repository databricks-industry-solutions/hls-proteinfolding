compute_mapping = {
    'azure': {
        'Standard_NC4as_T4_v3': 'Standard_NC4as_T4_v3',
        'Standard_D4ds_v5': 'Standard_D4ds_v5',
        'Standard_F8': 'Standard_F8'
    },
    'aws': {
        'Standard_NC4as_T4_v3': 'g4dn.2xlarge',
        'Standard_D4ds_v5': 'm5.xlarge',
        'Standard_F8': 'c4.2xlarge'
    },
}

af2_compute_mapping = {
  'azure': {
      'fold_compute' : "Standard_NC4as_T4_v3",
      'featurize_compute' : "Standard_F8"
  },
  'aws': {
      'fold_compute' : "g4dn.2xlarge",
      'featurize_compute' : "c4.2xlarge"
  }
}