# Polaris ground truth: volume 950-2400 mm along the tracker axis

## Raw tracker stream

| session | recordings | distance mm (median of medians) | off-axis deg | < 950 mm % | noise marker mm | **noise US image mm** | spikes /min |
|---|---|---|---|---|---|---|---|
| train_3XX | 7 | 927 | 2 | 80 | 0.169 | **0.238** | 6.1 |
| train_4XX | 32 | 879 | 8 | 86 | 0.175 | **0.249** | 8.2 |
| train_5XX | 41 | 903 | 5 | 97 | 0.080 | **0.115** | 0.0 |

### train_3XX

| recording | source | meas./s | distance mm p5 / median / p95 | off-axis deg median / p95 | < 950 mm % | > 2400 mm % | noise marker mm | **noise US image mm** | spikes > 1 mm /min |
|---|---|---|---|---|---|---|---|---|---|
| room-301 | pose.csv | 18 | 892 / 941 / 984 | 1 / 4 | 66 | 0 | 0.192 | **0.238** | 3.0 |
| room-302 | pose.csv | 20 | 886 / 926 / 979 | 4 / 6 | 79 | 0 | 0.147 | **0.203** | 4.0 |
| run-313 | pose.csv | 20 | 907 / 915 / 953 | 4 / 5 | 89 | 0 | 0.198 | **0.323** | 21.9 |
| run-314 | pose.csv | 20 | 894 / 923 / 955 | 2 / 4 | 85 | 0 | 0.144 | **0.166** | 4.0 |
| run-315 | pose.csv | 20 | 917 / 929 / 944 | 4 / 5 | 100 | 0 | 0.169 | **0.221** | 6.1 |
| run-316 | pose.csv | 20 | 898 / 927 / 958 | 2 / 4 | 85 | 0 | 0.153 | **0.267** | 17.9 |
| run-317 | pose.csv | 16 | 905 / 945 / 982 | 2 / 5 | 59 | 0 | 0.228 | **0.268** | 9.9 |

### train_4XX

| recording | source | meas./s | distance mm p5 / median / p95 | off-axis deg median / p95 | < 950 mm % | > 2400 mm % | noise marker mm | **noise US image mm** | spikes > 1 mm /min |
|---|---|---|---|---|---|---|---|---|---|
| room-401 | pose.csv | 20 | 777 / 878 / 968 | 3 / 9 | 87 | 0 | 0.210 | **0.344** | 11.9 |
| room-402 | pose.csv | 20 | 842 / 939 / 1010 | 4 / 7 | 59 | 0 | 0.215 | **0.343** | 5.8 |
| room-403 | pose.csv | 20 | 760 / 873 / 951 | 8 / 12 | 94 | 0 | 0.125 | **0.250** | 1.5 |
| room-404 | pose.csv | 20 | 813 / 881 / 971 | 8 / 10 | 92 | 0 | 0.121 | **0.233** | 0.0 |
| room-405 | pose.csv | 20 | 720 / 817 / 921 | 8 / 10 | 100 | 0 | 0.148 | **0.267** | 0.0 |
| room-406 | pose.csv | 20 | 789 / 882 / 936 | 9 / 10 | 100 | 0 | 0.127 | **0.228** | 1.5 |
| run-401 | pose.csv | 20 | 773 / 838 / 893 | 8 / 10 | 100 | 0 | 0.321 | **0.333** | 20.9 |
| run-402 | pose.csv | 20 | 907 / 934 / 1010 | 8 / 8 | 67 | 0 | 0.426 | **0.568** | 49.0 |
| run-403 | pose.csv | 20 | 895 / 905 / 966 | 8 / 9 | 84 | 0 | 0.165 | **0.210** | 9.0 |
| run-404 | pose.csv | 20 | 874 / 902 / 949 | 10 / 12 | 95 | 0 | 0.341 | **0.428** | 30.1 |
| run-405 | pose.csv | 20 | 869 / 900 / 990 | 8 / 10 | 76 | 0 | 0.253 | **0.461** | 19.5 |
| run-406 | pose.csv | 20 | 828 / 850 / 919 | 6 / 8 | 100 | 0 | 0.192 | **0.244** | 12.0 |
| run-407 | pose.csv | 20 | 837 / 851 / 870 | 7 / 8 | 100 | 0 | 0.171 | **0.210** | 5.9 |
| run-408 | pose.csv | 20 | 843 / 853 / 872 | 8 / 9 | 100 | 0 | 0.177 | **0.269** | 10.5 |
| run-409 | pose.csv | 20 | 847 / 852 / 935 | 9 / 9 | 100 | 0 | 0.220 | **0.311** | 16.1 |
| run-410 | pose.csv | 20 | 788 / 800 / 902 | 8 / 9 | 100 | 0 | 0.203 | **0.295** | 16.6 |
| run-411 | pose.csv | 20 | 802 / 819 / 835 | 10 / 11 | 100 | 0 | 0.136 | **0.190** | 4.5 |
| run-412 | pose.csv | 20 | 825 / 849 / 930 | 8 / 9 | 100 | 0 | 0.181 | **0.242** | 10.5 |
| run-413 | pose.csv | 20 | 805 / 839 / 902 | 8 / 9 | 100 | 0 | 0.291 | **0.296** | 19.5 |
| run-414 | pose.csv | 20 | 827 / 852 / 941 | 7 / 8 | 100 | 0 | 0.159 | **0.251** | 6.0 |
| run-415 | pose.csv | 20 | 833 / 853 / 891 | 8 / 9 | 100 | 0 | 0.173 | **0.195** | 4.5 |
| run-416 | pose.csv | 20 | 839 / 860 / 901 | 8 / 10 | 100 | 0 | 0.200 | **0.241** | 6.0 |
| run-418 | pose.csv | 20 | 891 / 933 / 1005 | 7 / 8 | 59 | 0 | 0.190 | **0.209** | 3.0 |
| run-419 | pose.csv | 20 | 893 / 919 / 994 | 8 / 10 | 73 | 0 | 0.171 | **0.218** | 6.0 |
| run-420 | pose.csv | 20 | 925 / 966 / 1008 | 8 / 9 | 33 | 0 | 0.162 | **0.247** | 9.0 |
| run-421 | pose.csv | 20 | 888 / 957 / 1003 | 6 / 9 | 39 | 0 | 0.180 | **0.383** | 16.3 |
| run-423 | pose.csv | 20 | 894 / 931 / 944 | 7 / 8 | 100 | 0 | 0.176 | **0.284** | 10.4 |
| run-424 | pose.csv | 20 | 890 / 929 / 990 | 7 / 9 | 62 | 0 | 0.131 | **0.173** | 0.0 |
| run-425 | pose.csv | 20 | 870 / 916 / 959 | 7 / 9 | 90 | 0 | 0.152 | **0.213** | 1.5 |
| run-426 | pose.csv | 20 | 822 / 879 / 942 | 7 / 9 | 100 | 0 | 0.159 | **0.234** | 7.5 |
| run-427 | pose.csv | 20 | 916 / 947 / 988 | 6 / 9 | 54 | 0 | 0.173 | **0.322** | 9.0 |
| run-428 | pose.csv | 20 | 812 / 877 / 946 | 7 / 8 | 100 | 0 | 0.173 | **0.220** | 3.0 |

### train_5XX

| recording | source | meas./s | distance mm p5 / median / p95 | off-axis deg median / p95 | < 950 mm % | > 2400 mm % | noise marker mm | **noise US image mm** | spikes > 1 mm /min |
|---|---|---|---|---|---|---|---|---|---|
| room-501 | pose.csv | 20 | 801 / 857 / 900 | 3 / 10 | 100 | 0 | 0.153 | **0.251** | 3.3 |
| room-502 | pose.csv | 20 | 845 / 921 / 942 | 5 / 6 | 98 | 0 | 0.126 | **0.182** | 2.6 |
| room-503 | pose.csv | 20 | 847 / 900 / 937 | 6 / 6 | 100 | 0 | 0.087 | **0.119** | 0.0 |
| room-504 | pose.csv | 19 | 841 / 897 / 940 | 5 / 6 | 99 | 0 | 0.100 | **0.167** | 1.3 |
| room-505 | pose.csv | 20 | 843 / 892 / 931 | 6 / 6 | 100 | 0 | 0.110 | **0.129** | 0.0 |
| room-506 | pose.csv | 20 | 841 / 897 / 928 | 6 / 7 | 100 | 0 | 0.098 | **0.128** | 0.0 |
| room-507 | pose.csv | 20 | 841 / 901 / 925 | 6 / 6 | 100 | 0 | 0.092 | **0.122** | 0.0 |
| room-508 | pose.csv | 20 | 833 / 885 / 930 | 6 / 6 | 100 | 0 | 0.131 | **0.179** | 1.3 |
| room-509 | pose.csv | 20 | 861 / 904 / 942 | 5 / 6 | 100 | 0 | 0.074 | **0.110** | 0.0 |
| run-501 | pose.csv | 20 | 832 / 865 / 943 | 6 / 6 | 100 | 0 | 0.073 | **0.107** | 0.0 |
| run-502 | pose.csv | 20 | 852 / 909 / 949 | 5 / 6 | 95 | 0 | 0.082 | **0.116** | 0.0 |
| run-503 | pose.csv | 20 | 832 / 873 / 928 | 5 / 6 | 100 | 0 | 0.084 | **0.107** | 0.0 |
| run-504 | pose.csv | 20 | 827 / 915 / 937 | 6 / 7 | 100 | 0 | 0.101 | **0.124** | 0.0 |
| run-505 | pose.csv | 20 | 909 / 923 / 952 | 5 / 6 | 93 | 0 | 0.092 | **0.124** | 0.0 |
| run-506 | pose.csv | 20 | 839 / 875 / 936 | 6 / 6 | 100 | 0 | 0.081 | **0.115** | 0.0 |
| run-507 | pose.csv | 20 | 832 / 876 / 932 | 6 / 6 | 100 | 0 | 0.075 | **0.104** | 0.0 |
| run-508 | pose.csv | 20 | 842 / 900 / 940 | 6 / 6 | 100 | 0 | 0.058 | **0.099** | 0.0 |
| run-509 | pose.csv | 20 | 838 / 904 / 940 | 6 / 6 | 100 | 0 | 0.080 | **0.127** | 0.0 |
| run-510 | pose.csv | 20 | 840 / 902 / 948 | 6 / 6 | 98 | 0 | 0.072 | **0.115** | 0.0 |
| run-511 | pose.csv | 20 | 841 / 919 / 941 | 6 / 6 | 100 | 0 | 0.061 | **0.118** | 0.0 |
| run-512 | pose.csv | 20 | 856 / 920 / 943 | 5 / 6 | 100 | 0 | 0.080 | **0.122** | 0.0 |
| run-513 | pose.csv | 20 | 858 / 917 / 951 | 5 / 6 | 95 | 0 | 0.082 | **0.115** | 0.0 |
| run-514 | pose.csv | 20 | 861 / 928 / 973 | 5 / 6 | 76 | 0 | 0.110 | **0.156** | 1.0 |
| run-515 | pose.csv | 20 | 861 / 926 / 968 | 5 / 6 | 75 | 0 | 0.079 | **0.125** | 0.0 |
| run-516 | pose.csv | 20 | 838 / 926 / 949 | 5 / 6 | 96 | 0 | 0.080 | **0.114** | 0.0 |
| run-517 | pose.csv | 20 | 848 / 893 / 950 | 5 / 6 | 94 | 0 | 0.062 | **0.095** | 0.0 |
| run-518 | pose.csv | 20 | 862 / 926 / 949 | 5 / 5 | 97 | 0 | 0.050 | **0.096** | 0.0 |
| run-519 | pose.csv | 20 | 838 / 900 / 952 | 5 / 6 | 93 | 0 | 0.059 | **0.092** | 0.0 |
| run-520 | pose.csv | 20 | 856 / 915 / 952 | 5 / 6 | 93 | 0 | 0.073 | **0.103** | 0.0 |
| run-521 | pose.csv | 20 | 864 / 936 / 957 | 5 / 5 | 81 | 0 | 0.057 | **0.113** | 0.0 |
| run-522 | pose.csv | 20 | 845 / 903 / 948 | 5 / 6 | 100 | 0 | 0.056 | **0.110** | 0.0 |
| run-523 | pose.csv | 20 | 853 / 911 / 960 | 5 / 7 | 93 | 0 | 0.071 | **0.119** | 0.0 |
| run-524 | pose.csv | 20 | 825 / 874 / 946 | 6 / 6 | 97 | 0 | 0.065 | **0.106** | 0.0 |
| run-525 | pose.csv | 20 | 851 / 889 / 929 | 6 / 6 | 100 | 0 | 0.093 | **0.114** | 0.0 |
| run-526 | pose.csv | 20 | 844 / 905 / 939 | 5 / 6 | 100 | 0 | 0.099 | **0.112** | 0.0 |
| run-527 | pose.csv | 20 | 835 / 899 / 934 | 6 / 6 | 100 | 0 | 0.098 | **0.160** | 2.0 |
| run-528 | pose.csv | 20 | 832 / 885 / 931 | 6 / 6 | 100 | 0 | 0.097 | **0.123** | 0.0 |
| run-529 | pose.csv | 20 | 857 / 916 / 955 | 5 / 6 | 91 | 0 | 0.068 | **0.102** | 0.0 |
| run-530 | pose.csv | 16 | 837 / 904 / 934 | 5 / 6 | 100 | 0 | 0.066 | **0.102** | 0.0 |
| run-531 | pose.csv | 20 | 846 / 898 / 942 | 5 / 6 | 98 | 0 | 0.109 | **0.213** | 7.1 |
| run-532 | pose.csv | 20 | 853 / 905 / 950 | 5 / 6 | 95 | 0 | 0.062 | **0.100** | 0.0 |

## Warnings

- train_3XX/room-301: 66 % of the samples nearer than 950 mm, 0 % farther than 2400 mm (outside the Polaris volume)
- train_3XX/room-302: 79 % of the samples nearer than 950 mm, 0 % farther than 2400 mm (outside the Polaris volume)
- train_3XX/run-313: 89 % of the samples nearer than 950 mm, 0 % farther than 2400 mm (outside the Polaris volume)
- train_3XX/run-314: 85 % of the samples nearer than 950 mm, 0 % farther than 2400 mm (outside the Polaris volume)
- train_3XX/run-315: 100 % of the samples nearer than 950 mm, 0 % farther than 2400 mm (outside the Polaris volume)
- train_3XX/run-316: 85 % of the samples nearer than 950 mm, 0 % farther than 2400 mm (outside the Polaris volume)
- train_3XX/run-317: 59 % of the samples nearer than 950 mm, 0 % farther than 2400 mm (outside the Polaris volume)
- train_4XX/room-401: 87 % of the samples nearer than 950 mm, 0 % farther than 2400 mm (outside the Polaris volume)
- train_4XX/room-402: 59 % of the samples nearer than 950 mm, 0 % farther than 2400 mm (outside the Polaris volume)
- train_4XX/room-403: 94 % of the samples nearer than 950 mm, 0 % farther than 2400 mm (outside the Polaris volume)
- train_4XX/room-404: 92 % of the samples nearer than 950 mm, 0 % farther than 2400 mm (outside the Polaris volume)
- train_4XX/room-405: 100 % of the samples nearer than 950 mm, 0 % farther than 2400 mm (outside the Polaris volume)
- train_4XX/room-406: 100 % of the samples nearer than 950 mm, 0 % farther than 2400 mm (outside the Polaris volume)
- train_4XX/run-401: 100 % of the samples nearer than 950 mm, 0 % farther than 2400 mm (outside the Polaris volume)
- train_4XX/run-402: 67 % of the samples nearer than 950 mm, 0 % farther than 2400 mm (outside the Polaris volume)
- train_4XX/run-403: 84 % of the samples nearer than 950 mm, 0 % farther than 2400 mm (outside the Polaris volume)
- train_4XX/run-404: 95 % of the samples nearer than 950 mm, 0 % farther than 2400 mm (outside the Polaris volume)
- train_4XX/run-405: 76 % of the samples nearer than 950 mm, 0 % farther than 2400 mm (outside the Polaris volume)
- train_4XX/run-406: 100 % of the samples nearer than 950 mm, 0 % farther than 2400 mm (outside the Polaris volume)
- train_4XX/run-407: 100 % of the samples nearer than 950 mm, 0 % farther than 2400 mm (outside the Polaris volume)
- train_4XX/run-408: 100 % of the samples nearer than 950 mm, 0 % farther than 2400 mm (outside the Polaris volume)
- train_4XX/run-409: 100 % of the samples nearer than 950 mm, 0 % farther than 2400 mm (outside the Polaris volume)
- train_4XX/run-410: 100 % of the samples nearer than 950 mm, 0 % farther than 2400 mm (outside the Polaris volume)
- train_4XX/run-411: 100 % of the samples nearer than 950 mm, 0 % farther than 2400 mm (outside the Polaris volume)
- train_4XX/run-412: 100 % of the samples nearer than 950 mm, 0 % farther than 2400 mm (outside the Polaris volume)
- train_4XX/run-413: 100 % of the samples nearer than 950 mm, 0 % farther than 2400 mm (outside the Polaris volume)
- train_4XX/run-414: 100 % of the samples nearer than 950 mm, 0 % farther than 2400 mm (outside the Polaris volume)
- train_4XX/run-415: 100 % of the samples nearer than 950 mm, 0 % farther than 2400 mm (outside the Polaris volume)
- train_4XX/run-416: 100 % of the samples nearer than 950 mm, 0 % farther than 2400 mm (outside the Polaris volume)
- train_4XX/run-418: 59 % of the samples nearer than 950 mm, 0 % farther than 2400 mm (outside the Polaris volume)
- train_4XX/run-419: 73 % of the samples nearer than 950 mm, 0 % farther than 2400 mm (outside the Polaris volume)
- train_4XX/run-420: 33 % of the samples nearer than 950 mm, 0 % farther than 2400 mm (outside the Polaris volume)
- train_4XX/run-421: 39 % of the samples nearer than 950 mm, 0 % farther than 2400 mm (outside the Polaris volume)
- train_4XX/run-423: 100 % of the samples nearer than 950 mm, 0 % farther than 2400 mm (outside the Polaris volume)
- train_4XX/run-424: 62 % of the samples nearer than 950 mm, 0 % farther than 2400 mm (outside the Polaris volume)
- train_4XX/run-425: 90 % of the samples nearer than 950 mm, 0 % farther than 2400 mm (outside the Polaris volume)
- train_4XX/run-426: 100 % of the samples nearer than 950 mm, 0 % farther than 2400 mm (outside the Polaris volume)
- train_4XX/run-427: 54 % of the samples nearer than 950 mm, 0 % farther than 2400 mm (outside the Polaris volume)
- train_4XX/run-428: 100 % of the samples nearer than 950 mm, 0 % farther than 2400 mm (outside the Polaris volume)
- train_5XX/room-501: 100 % of the samples nearer than 950 mm, 0 % farther than 2400 mm (outside the Polaris volume)
- train_5XX/room-502: 98 % of the samples nearer than 950 mm, 0 % farther than 2400 mm (outside the Polaris volume)
- train_5XX/room-503: 100 % of the samples nearer than 950 mm, 0 % farther than 2400 mm (outside the Polaris volume)
- train_5XX/room-504: 99 % of the samples nearer than 950 mm, 0 % farther than 2400 mm (outside the Polaris volume)
- train_5XX/room-505: 100 % of the samples nearer than 950 mm, 0 % farther than 2400 mm (outside the Polaris volume)
- train_5XX/room-506: 100 % of the samples nearer than 950 mm, 0 % farther than 2400 mm (outside the Polaris volume)
- train_5XX/room-507: 100 % of the samples nearer than 950 mm, 0 % farther than 2400 mm (outside the Polaris volume)
- train_5XX/room-508: 100 % of the samples nearer than 950 mm, 0 % farther than 2400 mm (outside the Polaris volume)
- train_5XX/room-509: 100 % of the samples nearer than 950 mm, 0 % farther than 2400 mm (outside the Polaris volume)
- train_5XX/run-501: 100 % of the samples nearer than 950 mm, 0 % farther than 2400 mm (outside the Polaris volume)
- train_5XX/run-502: 95 % of the samples nearer than 950 mm, 0 % farther than 2400 mm (outside the Polaris volume)
- train_5XX/run-503: 100 % of the samples nearer than 950 mm, 0 % farther than 2400 mm (outside the Polaris volume)
- train_5XX/run-504: 100 % of the samples nearer than 950 mm, 0 % farther than 2400 mm (outside the Polaris volume)
- train_5XX/run-505: 93 % of the samples nearer than 950 mm, 0 % farther than 2400 mm (outside the Polaris volume)
- train_5XX/run-506: 100 % of the samples nearer than 950 mm, 0 % farther than 2400 mm (outside the Polaris volume)
- train_5XX/run-507: 100 % of the samples nearer than 950 mm, 0 % farther than 2400 mm (outside the Polaris volume)
- train_5XX/run-508: 100 % of the samples nearer than 950 mm, 0 % farther than 2400 mm (outside the Polaris volume)
- train_5XX/run-509: 100 % of the samples nearer than 950 mm, 0 % farther than 2400 mm (outside the Polaris volume)
- train_5XX/run-510: 98 % of the samples nearer than 950 mm, 0 % farther than 2400 mm (outside the Polaris volume)
- train_5XX/run-511: 100 % of the samples nearer than 950 mm, 0 % farther than 2400 mm (outside the Polaris volume)
- train_5XX/run-512: 100 % of the samples nearer than 950 mm, 0 % farther than 2400 mm (outside the Polaris volume)
- train_5XX/run-513: 95 % of the samples nearer than 950 mm, 0 % farther than 2400 mm (outside the Polaris volume)
- train_5XX/run-514: 76 % of the samples nearer than 950 mm, 0 % farther than 2400 mm (outside the Polaris volume)
- train_5XX/run-515: 75 % of the samples nearer than 950 mm, 0 % farther than 2400 mm (outside the Polaris volume)
- train_5XX/run-516: 96 % of the samples nearer than 950 mm, 0 % farther than 2400 mm (outside the Polaris volume)
- train_5XX/run-517: 94 % of the samples nearer than 950 mm, 0 % farther than 2400 mm (outside the Polaris volume)
- train_5XX/run-518: 97 % of the samples nearer than 950 mm, 0 % farther than 2400 mm (outside the Polaris volume)
- train_5XX/run-519: 93 % of the samples nearer than 950 mm, 0 % farther than 2400 mm (outside the Polaris volume)
- train_5XX/run-520: 93 % of the samples nearer than 950 mm, 0 % farther than 2400 mm (outside the Polaris volume)
- train_5XX/run-521: 81 % of the samples nearer than 950 mm, 0 % farther than 2400 mm (outside the Polaris volume)
- train_5XX/run-522: 100 % of the samples nearer than 950 mm, 0 % farther than 2400 mm (outside the Polaris volume)
- train_5XX/run-523: 93 % of the samples nearer than 950 mm, 0 % farther than 2400 mm (outside the Polaris volume)
- train_5XX/run-524: 97 % of the samples nearer than 950 mm, 0 % farther than 2400 mm (outside the Polaris volume)
- train_5XX/run-525: 100 % of the samples nearer than 950 mm, 0 % farther than 2400 mm (outside the Polaris volume)
- train_5XX/run-526: 100 % of the samples nearer than 950 mm, 0 % farther than 2400 mm (outside the Polaris volume)
- train_5XX/run-527: 100 % of the samples nearer than 950 mm, 0 % farther than 2400 mm (outside the Polaris volume)
- train_5XX/run-528: 100 % of the samples nearer than 950 mm, 0 % farther than 2400 mm (outside the Polaris volume)
- train_5XX/run-529: 91 % of the samples nearer than 950 mm, 0 % farther than 2400 mm (outside the Polaris volume)
- train_5XX/run-530: 100 % of the samples nearer than 950 mm, 0 % farther than 2400 mm (outside the Polaris volume)
- train_5XX/run-531: 98 % of the samples nearer than 950 mm, 0 % farther than 2400 mm (outside the Polaris volume)
- train_5XX/run-532: 95 % of the samples nearer than 950 mm, 0 % farther than 2400 mm (outside the Polaris volume)
