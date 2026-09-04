"""
build_idas_v4.py
Generates the perfect Agri-IDAS index.html:
  - EXACT previous UI structure (sidebar, tab-bar, KPI cards, safety alert, IoT telemetry)
  - NEW features: dual OSRM routing toggle, fuel cost calculator, CartoDB tiles, robust NLP
  - ROAD-SNAPPED route using embedded 1,313 OSRM centerline points + live OSRM fallback
"""

# ── 1,313 OSRM Road-Centerline Coordinates (Mithi → Hyderabad) ─────
# These are actual road-matched coordinates — polyline snaps pixel-perfect onto OSM roads
OSRM_COORDS = """[[24.743671,69.796077],[24.743647,69.795988],[24.74351,69.79564],[24.743363,69.795264],[24.743024,69.794397],[24.742993,69.794376],[24.742964,69.794373],[24.742594,69.794526],[24.742462,69.794408],[24.742294,69.794169],[24.742104,69.793772],[24.742007,69.793543],[24.741882,69.793169],[24.741879,69.7931],[24.741936,69.793084],[24.742333,69.792968],[24.742431,69.792913],[24.742504,69.792893],[24.742957,69.792769],[24.744126,69.792449],[24.74556,69.792056],[24.745598,69.792045],[24.746647,69.791758],[24.746845,69.791703],[24.747227,69.791599],[24.747327,69.791568],[24.747378,69.791554],[24.747739,69.791458],[24.748228,69.791324],[24.748925,69.791133],[24.749779,69.790899],[24.749863,69.790905],[24.750173,69.79081],[24.750445,69.790727],[24.750587,69.790636],[24.752997,69.789833],[24.753324,69.789724],[24.753993,69.789501],[24.754197,69.789433],[24.755447,69.789016],[24.755902,69.788836],[24.756321,69.788649],[24.756476,69.788559],[24.756667,69.788407],[24.756813,69.788262],[24.756942,69.788093],[24.757115,69.787855],[24.757415,69.787337],[24.758187,69.786202],[24.758365,69.785972],[24.758513,69.785776],[24.758874,69.785357],[24.759044,69.785165],[24.759203,69.785017],[24.759337,69.784901],[24.759502,69.784786],[24.759836,69.784555],[24.76023,69.784263],[24.760866,69.783791],[24.761926,69.783011],[24.762196,69.782793],[24.763265,69.781991],[24.763769,69.781576],[24.763989,69.781417],[24.764115,69.781318],[24.764235,69.781224],[24.764459,69.781028],[24.7647,69.780806],[24.764834,69.780647],[24.765036,69.780363],[24.765447,69.77977],[24.765648,69.779498],[24.765936,69.779125],[24.766239,69.778711],[24.766698,69.77811],[24.766947,69.777811],[24.767101,69.777626],[24.767174,69.777568],[24.767688,69.777032],[24.767894,69.776815],[24.769426,69.775326],[24.769791,69.775018],[24.769939,69.7749],[24.770237,69.774735],[24.771868,69.773875],[24.775355,69.772166],[24.776953,69.771929],[24.778393,69.771745],[24.779911,69.771543],[24.780775,69.771275],[24.785045,69.769896],[24.786263,69.769524],[24.786753,69.76929],[24.786989,69.769176],[24.787488,69.768666],[24.787619,69.768532],[24.787758,69.76839],[24.787898,69.768195],[24.788445,69.767285],[24.788736,69.766734],[24.788883,69.766407],[24.78932,69.765224],[24.789586,69.764052],[24.789799,69.761793],[24.790029,69.759404],[24.7904,69.757135],[24.790561,69.756073],[24.790705,69.754017],[24.790771,69.753542],[24.791375,69.751772],[24.792377,69.749357],[24.793009,69.748259],[24.793751,69.747173],[24.794122,69.746746],[24.796758,69.745361],[24.797328,69.745105],[24.797671,69.744757],[24.798541,69.742287],[24.799056,69.740219],[24.799344,69.739407],[24.800163,69.737742],[24.800634,69.736992],[24.800784,69.736583],[24.801033,69.735491],[24.801221,69.73507],[24.802661,69.733124],[24.803519,69.731837],[24.803724,69.731361],[24.803785,69.730897],[24.803935,69.729488],[24.803992,69.729175],[24.804636,69.726646],[24.805744,69.722169],[24.80662,69.718265],[24.807387,69.714747],[24.80773,69.712715],[24.807866,69.711686],[24.808013,69.711083],[24.808268,69.710418],[24.808691,69.709833],[24.809566,69.70923],[24.811892,69.707955],[24.813812,69.706667],[24.814975,69.705797],[24.815415,69.705274],[24.816674,69.703794],[24.816996,69.70347],[24.818644,69.702649],[24.819056,69.702295],[24.819666,69.701524],[24.821105,69.69934],[24.821472,69.698774],[24.821659,69.698333],[24.821845,69.697642],[24.821964,69.695888],[24.822031,69.69526],[24.822195,69.694452],[24.82228,69.693842],[24.822545,69.690172],[24.822618,69.689376],[24.822788,69.688686],[24.823228,69.687504],[24.823544,69.687013],[24.826245,69.684298],[24.827583,69.68317],[24.828145,69.682832],[24.829292,69.682352],[24.829956,69.681988],[24.831968,69.680845],[24.834038,69.679811],[24.835291,69.679136],[24.836022,69.678577],[24.837779,69.677267],[24.838068,69.676955],[24.838145,69.67663],[24.838401,69.674977],[24.838607,69.674096],[24.838729,69.673484],[24.839351,69.670178],[24.839707,69.668617],[24.840118,69.667325],[24.840173,69.666933],[24.840196,69.666535],[24.840079,69.665604],[24.839584,69.662788],[24.839262,69.660413],[24.839023,69.658901],[24.838684,69.657266],[24.838512,69.656334],[24.838449,69.655672],[24.838436,69.654956],[24.838569,69.653316],[24.838674,69.651497],[24.838712,69.650714],[24.838912,69.64901],[24.839038,69.647702],[24.83915,69.646984],[24.839155,69.646389],[24.839067,69.645726],[24.838314,69.642304],[24.838047,69.641056],[24.837917,69.640651],[24.837115,69.638772],[24.836166,69.636543],[24.835991,69.636119],[24.835924,69.635732],[24.835899,69.635382],[24.835828,69.632269],[24.835798,69.632025],[24.835765,69.631772],[24.833663,69.627581],[24.831832,69.624555],[24.831272,69.62374],[24.829784,69.622031],[24.829483,69.621649],[24.829295,69.621446],[24.829065,69.621078],[24.82891,69.620714],[24.828835,69.62041],[24.828626,69.618646],[24.828614,69.618301],[24.828668,69.617831],[24.828781,69.617274],[24.828885,69.616928],[24.829178,69.616321],[24.829475,69.615901],[24.830515,69.614962],[24.831213,69.61446],[24.831974,69.614055],[24.832233,69.613847],[24.832472,69.613539],[24.832731,69.613069],[24.832877,69.612793],[24.833399,69.609928],[24.833437,69.609463],[24.833391,69.608915],[24.833324,69.608372],[24.833345,69.606387],[24.83337,69.605093],[24.833441,69.604729],[24.83373,69.603881],[24.834323,69.601836],[24.834917,69.600381],[24.835857,69.597811],[24.836258,69.596612],[24.83643,69.596098],[24.836526,69.595601],[24.836572,69.594615],[24.836659,69.593777],[24.837061,69.590839],[24.837123,69.590461],[24.837249,69.590097],[24.837809,69.588596],[24.838126,69.588048],[24.839836,69.586017],[24.841177,69.584396],[24.842745,69.582715],[24.843656,69.581605],[24.843835,69.581158],[24.844032,69.580647],[24.844922,69.579099],[24.845482,69.57799],[24.845578,69.57769],[24.845674,69.57699],[24.845762,69.576272],[24.8458,69.575926],[24.845745,69.575314],[24.845632,69.574356],[24.845616,69.573458],[24.845653,69.57297],[24.845812,69.572306],[24.845862,69.571883],[24.845887,69.571266],[24.84577,69.570672],[24.845591,69.569861],[24.845377,69.568608],[24.845156,69.56759],[24.845093,69.56724],[24.844997,69.56655],[24.844818,69.565935],[24.844605,69.565397],[24.844358,69.564878],[24.843802,69.564048],[24.843647,69.563841],[24.843457,69.563552],[24.843134,69.562909],[24.842978,69.562469],[24.84281,69.561934],[24.842695,69.560829],[24.842585,69.559043],[24.842547,69.558254],[24.842475,69.557056],[24.842443,69.556327],[24.842437,69.555763],[24.842496,69.55429],[24.842552,69.55324],[24.842597,69.552493],[24.842657,69.552119],[24.842743,69.55181],[24.842858,69.551432],[24.843023,69.551024],[24.843748,69.549758],[24.844145,69.548888],[24.844245,69.548588],[24.844901,69.545756],[24.844955,69.545498],[24.84495,69.545386],[24.844884,69.544061],[24.844879,69.543991],[24.844692,69.541561],[24.844638,69.539857],[24.844621,69.538535],[24.844671,69.538037],[24.844964,69.536126],[24.845152,69.534763],[24.845256,69.534353],[24.84549,69.533782],[24.845574,69.533464],[24.845858,69.532288],[24.845871,69.532235],[24.84595,69.531843],[24.846368,69.529034],[24.846615,69.527588],[24.846903,69.52587],[24.847045,69.524714],[24.847162,69.523503],[24.847179,69.52312],[24.846786,69.520173],[24.846585,69.518626],[24.846535,69.518156],[24.84661,69.516949],[24.846615,69.516895],[24.846732,69.515374],[24.846936,69.512537],[24.846928,69.512242],[24.846606,69.509511],[24.846518,69.509028],[24.845077,69.50579],[24.844734,69.505215],[24.844195,69.504459],[24.844023,69.504183],[24.842565,69.500643],[24.842475,69.500318],[24.842442,69.499936],[24.842433,69.499484],[24.842416,69.499342],[24.844816,69.499037],[24.844892,69.499029],[24.846671,69.498823],[24.846988,69.498825],[24.84728,69.498865],[24.848138,69.499021],[24.848303,69.499052],[24.85201,69.499775],[24.853727,69.500118],[24.854188,69.500229],[24.854255,69.500236],[24.840854,69.49512],[24.840695,69.494807],[24.839779,69.493006],[24.838893,69.491284],[24.838776,69.490975],[24.838513,69.490151],[24.838258,69.48935],[24.837443,69.486817],[24.836787,69.484689],[24.836674,69.484371],[24.836557,69.483957],[24.836494,69.483482],[24.836074,69.47514],[24.836058,69.474825],[24.835946,69.474466],[24.835626,69.473705],[24.835159,69.473086],[24.834858,69.472598],[24.834793,69.47222],[24.834775,69.471803],[24.83484,69.471334],[24.835028,69.47094],[24.835094,69.4708],[24.835833,69.469804],[24.836099,69.469231],[24.83774,69.46476],[24.839283,69.460677],[24.840849,69.456736],[24.841783,69.454203],[24.841925,69.453747],[24.842185,69.451702],[24.842398,69.450679],[24.842469,69.450034],[24.842522,69.449344],[24.842551,69.448061],[24.842498,69.446595],[24.842664,69.445586],[24.842758,69.444895],[24.842803,69.443433],[24.842924,69.439444],[24.843075,69.435538],[24.843142,69.433413],[24.843355,69.428867],[24.84345,69.428202],[24.843586,69.42744],[24.843946,69.425493],[24.844189,69.424457],[24.845495,69.420491],[24.845861,69.419475],[24.846287,69.418166],[24.846446,69.417618],[24.846637,69.416904],[24.84674,69.416424],[24.846807,69.416127],[24.846888,69.415884],[24.847014,69.415587],[24.847515,69.414516],[24.848029,69.413495],[24.848818,69.412165],[24.849279,69.411416],[24.850204,69.410269],[24.851643,69.408687],[24.852189,69.408097],[24.852467,69.407648],[24.853141,69.406287],[24.853475,69.405602],[24.853853,69.404828],[24.854231,69.4039],[24.854666,69.403248],[24.855047,69.402603],[24.855567,69.401395],[24.856172,69.399959],[24.856763,69.398881],[24.857046,69.398395],[24.857405,69.397776],[24.858167,69.396465],[24.860997,69.391723],[24.861724,69.390498],[24.862304,69.389505],[24.863938,69.386706],[24.864327,69.38604],[24.864957,69.38498],[24.865694,69.383742],[24.866839,69.381771],[24.872134,69.372742],[24.874319,69.369089],[24.87866,69.362609],[24.884705,69.353772],[24.889175,69.347303],[24.889469,69.346906],[24.890209,69.345832],[24.893285,69.341408],[24.897175,69.335746],[24.899267,69.332705],[24.900078,69.331946],[24.902867,69.330185],[24.908198,69.326797],[24.910642,69.325246],[24.912465,69.324103],[24.913983,69.323389],[24.918554,69.32196],[24.921266,69.321001],[24.929083,69.31754],[24.938884,69.313124],[24.941436,69.311522],[24.946094,69.307684],[24.948763,69.305505],[24.949915,69.304797],[24.95119,69.304268],[24.953345,69.303276],[24.956997,69.301696],[24.959066,69.301323],[24.962509,69.299917],[24.96402,69.299371],[24.96576,69.298762],[24.968744,69.297696],[24.970399,69.297104],[24.97298,69.29615],[24.975228,69.295374],[24.978007,69.294528],[24.982647,69.293457],[24.986388,69.292562],[24.990423,69.291653],[24.994549,69.290679],[24.997061,69.289936],[24.998042,69.28925],[24.999585,69.286746],[25.000398,69.285707],[25.001789,69.284199],[25.00514,69.280521],[25.008377,69.276919],[25.012878,69.272159],[25.014972,69.266047],[25.015305,69.264848],[25.016364,69.26121],[25.019877,69.257159],[25.023123,69.253581],[25.028068,69.248196],[25.031349,69.244593],[25.034631,69.240996],[25.039573,69.235604],[25.044472,69.230259],[25.047798,69.22663],[25.051595,69.222642],[25.052787,69.222012],[25.056525,69.220569],[25.0588,69.218441],[25.059761,69.217863],[25.061397,69.217682],[25.065063,69.217781],[25.06748,69.217748],[25.069042,69.217109],[25.07095,69.216218],[25.072303,69.215854],[25.073254,69.215201],[25.075107,69.212787],[25.076146,69.211561],[25.076649,69.210237],[25.077025,69.209556],[25.078732,69.207667],[25.079884,69.206406],[25.082795,69.203126],[25.08725,69.198251],[25.090069,69.19518],[25.095481,69.189217],[25.099219,69.185186],[25.100454,69.180013],[25.100702,69.17709],[25.101181,69.172233],[25.101277,69.171809],[25.103453,69.169168],[25.105113,69.167378],[25.107988,69.16416],[25.11041,69.161534],[25.116614,69.15468],[25.118189,69.152966],[25.119736,69.151248],[25.128007,69.142135],[25.137785,69.131341],[25.144702,69.123668],[25.150812,69.116913],[25.15374,69.113683],[25.155549,69.111731],[25.155808,69.108218],[25.156041,69.107262],[25.156398,69.105875],[25.157304,69.102502],[25.157364,69.101595],[25.157356,69.073754],[25.157347,69.072797],[25.157266,69.070137],[25.157282,69.062856],[25.157259,69.053013],[25.157257,69.048654],[25.157255,69.045129],[25.157201,69.027153],[25.157065,69.027089],[25.152061,69.021623],[25.148504,69.017717],[25.146013,69.015035],[25.144532,69.01342],[25.143148,69.013828],[25.13784,69.019707],[25.133396,69.015582],[25.127413,69.017696],[25.122456,69.014303],[25.120875,69.012541],[25.118639,69.012495],[25.116295,69.012482],[25.113507,69.012057],[25.111489,69.012038],[25.111175,69.012946],[25.111234,69.015862],[25.11124,69.018104],[25.109873,69.018476],[25.107073,69.018471],[25.10457,69.018468],[25.102291,69.018464],[25.098794,69.018441],[25.096598,69.018393],[25.093217,69.018356],[25.093027,69.016414],[25.093022,69.014311],[25.093042,69.013131],[25.09309,69.012921],[25.095277,69.007992],[25.09551,69.0073],[25.095874,69.005508],[25.096209,69.004993],[25.102753,68.99678],[25.107967,68.990604],[25.109463,68.989043],[25.110075,68.988709],[25.111957,68.988325],[25.112206,68.987866],[25.112622,68.987057],[25.113294,68.986881],[25.114864,68.986928],[25.118029,68.986502],[25.119661,68.986008],[25.121177,68.985364],[25.122809,68.984678],[25.124616,68.983412],[25.12668,68.981593],[25.127569,68.980188],[25.128482,68.979185],[25.132153,68.975987],[25.135689,68.972189],[25.137087,68.970366],[25.139205,68.967576],[25.140953,68.965151],[25.144236,68.962083],[25.14645,68.959615],[25.148942,68.956872],[25.147567,68.954684],[25.147245,68.953458],[25.145951,68.948394],[25.14413,68.942737],[25.143242,68.939978],[25.141067,68.933388],[25.138803,68.928676],[25.13812,68.926905],[25.136859,68.923879],[25.135854,68.921838],[25.133855,68.91762],[25.132169,68.914553],[25.13082,68.912914],[25.12939,68.910869],[25.127325,68.907671],[25.126511,68.906451],[25.125498,68.90426],[25.124843,68.90254],[25.124783,68.898647],[25.124935,68.896924],[25.125367,68.895731],[25.125952,68.894863],[25.127066,68.893211],[25.128028,68.891795],[25.128796,68.889391],[25.128526,68.887643],[25.129705,68.885758],[25.1316,68.883467],[25.135344,68.878795],[25.13803,68.875496],[25.140018,68.873055],[25.143354,68.868959],[25.146581,68.864923],[25.149597,68.861189],[25.152272,68.857874],[25.15461,68.854993],[25.158906,68.849845],[25.160869,68.847473],[25.16269,68.8453],[25.165068,68.842452],[25.166532,68.840682],[25.168536,68.838174],[25.169968,68.83637],[25.17157,68.834361],[25.173092,68.832462],[25.175289,68.829692],[25.203577,68.790915],[25.207276,68.785819],[25.208911,68.783555],[25.211464,68.780009],[25.212542,68.778352],[25.213338,68.774639],[25.214431,68.769565],[25.216056,68.762151],[25.217143,68.756926],[25.218764,68.749485],[25.219657,68.744985],[25.220414,68.739706],[25.220918,68.734996],[25.221375,68.730458],[25.221879,68.725791],[25.222336,68.7218],[25.22251,68.720963],[25.223131,68.719665],[25.226315,68.713839],[25.227926,68.710492],[25.230323,68.706833],[25.233312,68.702531],[25.238223,68.695149],[25.241562,68.690168],[25.244861,68.685247],[25.251256,68.675398],[25.255477,68.668931],[25.257798,68.665573],[25.25931,68.663073],[25.260428,68.6623],[25.262165,68.661187],[25.262398,68.660766],[25.262448,68.65984],[25.261814,68.659038],[25.262914,68.65372],[25.263482,68.651585],[25.264234,68.647707],[25.265238,68.644365],[25.266063,68.642793],[25.269103,68.637598],[25.270267,68.635237],[25.271586,68.631826],[25.273158,68.627899],[25.276389,68.61952],[25.278998,68.612739],[25.280919,68.607825],[25.283451,68.601195],[25.285304,68.597279],[25.287468,68.593245],[25.289398,68.591196],[25.290692,68.590303],[25.296014,68.586807],[25.299835,68.5842],[25.303676,68.580853],[25.307275,68.577667],[25.30871,68.575081],[25.309544,68.573472],[25.310125,68.572122],[25.310396,68.571063],[25.311445,68.569105],[25.315771,68.562324],[25.319301,68.557164],[25.320203,68.555833],[25.322249,68.552797],[25.32577,68.547636],[25.327787,68.544708],[25.32992,68.541339],[25.331239,68.539236],[25.33373,68.535343],[25.336272,68.531393],[25.337309,68.529644],[25.338589,68.526683],[25.340248,68.522789],[25.341944,68.520847],[25.343438,68.519269],[25.344291,68.518261],[25.346996,68.514356],[25.349682,68.510397],[25.352028,68.507017],[25.353599,68.504477],[25.35485,68.502296],[25.356083,68.500642],[25.358224,68.497426],[25.361093,68.492941],[25.363808,68.488102],[25.366096,68.483124],[25.368016,68.478917],[25.370817,68.472824],[25.372376,68.469486],[25.375232,68.463327],[25.377244,68.458917],[25.378886,68.455435],[25.379705,68.453491],[25.38061,68.450315],[25.381583,68.446952],[25.382219,68.444766],[25.38392,68.438954],[25.384888,68.435642],[25.386488,68.431394],[25.386732,68.430574],[25.387048,68.428953],[25.387276,68.427695],[25.38745,68.426699],[25.387725,68.425097],[25.388472,68.420883],[25.38902,68.418331],[25.389432,68.416415],[25.389812,68.414456],[25.390113,68.412967],[25.390381,68.41099],[25.39086,68.408378],[25.39137,68.405791],[25.391639,68.405203],[25.391834,68.404536],[25.391886,68.403826],[25.391947,68.403153],[25.392609,68.403014],[25.39517,68.402485],[25.397751,68.401993],[25.398196,68.401868],[25.398883,68.401671],[25.40099,68.4012],[25.4024,68.400882],[25.403997,68.400254],[25.405582,68.399454],[25.406837,68.39861],[25.408362,68.397353],[25.410121,68.395578],[25.411152,68.394456],[25.4122,68.393073],[25.413033,68.391655],[25.413813,68.390066],[25.414471,68.388469],[25.4151,68.386953],[25.416325,68.38402],[25.417541,68.381004],[25.418109,68.379489],[25.418223,68.379121],[25.417622,68.378844],[25.41746,68.378801],[25.415985,68.378388],[25.41496,68.37807],[25.41448,68.377855],[25.413566,68.377502],[25.412617,68.377086],[25.411509,68.376436],[25.410786,68.375428],[25.409288,68.373501],[25.408962,68.372929],[25.408535,68.371153],[25.40844,68.370595],[25.407954,68.368119],[25.407694,68.366946],[25.407396,68.365532],[25.407128,68.36418],[25.406542,68.361564],[25.406409,68.360578],[25.405985,68.358196],[25.405636,68.356956],[25.405452,68.356654],[25.405228,68.35652],[25.404756,68.356736],[25.403194,68.357623],[25.402099,68.357939],[25.401547,68.358037],[25.40093,68.358213],[25.399984,68.358754],[25.398942,68.359599],[25.397369,68.358533],[25.396413,68.357876],[25.396056,68.357863]]"""

HTML = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Agri-Logistics IDAS · Phase 3 Research Portal</title>
<meta name="description" content="Agri-IDAS — Trilingual AI-powered logistics dispatch system for Sindh agricultural transport. Real-time GIS routing, NLP chatbot, IoT telemetry.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<style>
/* ─── DESIGN TOKENS ──────────────────────────────────── */
:root {
  --bg:          #F5F2EC;
  --primary:     #2D5016;
  --primary-dk:  #1E3A0F;
  --primary-lt:  #4A7C2F;
  --gold:        #D4AF37;
  --card-bg:     #FFFFFF;
  --text-dk:     #2D3A1F;
  --text-muted:  #5C6B4A;
  --border:      #EAE6DE;
}
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html { scroll-behavior: smooth; }
body { font-family: "Inter", sans-serif; background: var(--bg); color: var(--text-dk); line-height: 1.5; }
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #f1f1f1; }
::-webkit-scrollbar-thumb { background: #c4bdb0; border-radius: 3px; }

/* ─── LAYOUT ─────────────────────────────────────────── */
.app-layout { display: flex; min-height: 100vh; }
.sidebar {
  width: 300px; flex-shrink: 0;
  background: linear-gradient(180deg,#111A06 0%,#1E2E0A 60%,#2A3F10 100%);
  border-right: 1px solid #3A5215;
  padding: 22px 18px;
  color: #D0DEB8;
  overflow-y: auto;
}
.main-content { flex: 1; padding: 28px 32px; overflow-y: auto; }
@media(max-width:900px) {
  .app-layout { flex-direction: column; }
  .sidebar { width: 100%; }
  .grid-2 { grid-template-columns: 1fr !important; }
  .grid-kpi { grid-template-columns: repeat(2,1fr) !important; }
  .controls-row { grid-template-columns: repeat(2,1fr) !important; }
}

/* ─── SIDEBAR COMPONENTS ─────────────────────────────── */
.academic-card {
  background: linear-gradient(160deg,#1A2409 0%,#243310 100%);
  border: 1px solid #5A4A1A;
  border-left: 4px solid var(--gold);
  border-radius: 14px;
  padding: 18px; margin-bottom: 18px;
}
.ac-badge {
  background: var(--gold); color: #1A1000;
  font-size: 0.63rem; font-weight: 800;
  padding: 3px 10px; border-radius: 20px;
  letter-spacing: 1px; text-transform: uppercase;
  display: inline-block; margin-bottom: 10px;
}
.ac-name { color:#FFF; font-size:1.1rem; font-weight:800; margin-bottom:2px; }
.ac-id { color:var(--gold); font-size:0.76rem; font-weight:600; }
.ac-divider { border:none; border-top:1px solid #3A4F1A; margin:10px 0; }
.ac-row { display:flex; align-items:flex-start; gap:8px; font-size:0.73rem; margin-bottom:7px; color:#D0DEB8; }
.sidebar-section {
  background:#1A2409; border-radius:10px;
  padding:14px; margin-bottom:14px;
  font-size:0.73rem; line-height:1.7;
}
.sidebar-section h4 {
  color:#C8D8A0; font-size:0.76rem;
  text-transform:uppercase; letter-spacing:.8px;
  margin-bottom:8px;
  border-bottom:1px solid #2D4012; padding-bottom:4px;
}
.route-toggle-section { background:#1A2409; border-radius:10px; padding:14px; margin-bottom:14px; }
.route-toggle-section h4 { color:#C8D8A0; font-size:0.76rem; text-transform:uppercase; letter-spacing:.8px; margin-bottom:10px; border-bottom:1px solid #2D4012; padding-bottom:4px; }
.route-btn-group { display:flex; flex-direction:column; gap:8px; }
.route-option {
  display:flex; align-items:center; gap:10px;
  padding:10px 12px; border-radius:8px;
  border:1px solid #3A5215; background:#111A06;
  cursor:pointer; transition:all 0.2s;
}
.route-option.active { background:#1E3A0F; border-color:var(--primary-lt); }
.route-dot { width:10px; height:10px; border-radius:50%; flex-shrink:0; }
.route-dot.r1 { background:#4A7C2F; }
.route-dot.r2 { background:#3B82F6; }
.route-option-label { font-size:0.75rem; color:#C8D8A0; font-weight:600; }
.route-option-meta  { font-size:0.67rem; color:#7A9A60; margin-top:1px; }
.fuel-card {
  background: linear-gradient(135deg,#1A2409,#243310);
  border:1px solid #5A4A1A; border-left:4px solid var(--gold);
  border-radius:10px; padding:12px; margin-bottom:14px;
}
.fuel-card .fuel-label { color:#A0B880; font-size:0.67rem; text-transform:uppercase; letter-spacing:.8px; margin-bottom:3px; }
.fuel-card .fuel-value { color:var(--gold); font-size:1.3rem; font-weight:800; }
.fuel-card .fuel-note  { color:#7A9A60; font-size:0.67rem; margin-top:3px; }

/* ─── HEADER ─────────────────────────────────────────── */
.app-header {
  background: linear-gradient(135deg,#1E3A0F 0%,#2D5016 50%,#3D6B22 100%);
  border-radius:14px; padding:20px 28px;
  margin-bottom:22px;
  display:flex; align-items:center; justify-content:space-between;
  box-shadow:0 4px 20px rgba(45,80,22,.25); color:#FFF;
}
.app-header h1 { font-size:1.55rem; font-weight:800; letter-spacing:-.5px; }
.app-header p  { color:#C5DFA0; font-size:0.8rem; margin-top:3px; }
.header-badge {
  background:rgba(255,255,255,.15); border:1px solid rgba(255,255,255,.3);
  color:#FFF; font-size:0.68rem; font-weight:700;
  padding:4px 12px; border-radius:20px; letter-spacing:.8px;
}

/* ─── TAB BAR ────────────────────────────────────────── */
.tab-bar {
  display:flex; gap:10px;
  background:#E2DDD0; border-radius:12px;
  padding:6px; border:1px solid #C4BDAC;
  margin-bottom:22px;
}
.tab-btn {
  flex:1; padding:11px 20px; border-radius:8px;
  border:1px solid var(--primary-dk);
  background:var(--primary); color:#FFF;
  font-weight:700; font-size:0.88rem;
  cursor:pointer; transition:all 0.2s;
  display:flex; align-items:center; justify-content:center; gap:8px;
}
.tab-btn.active {
  background:#FFF !important; color:var(--primary-dk) !important;
  border:2px solid var(--primary) !important;
  box-shadow:0 4px 14px rgba(0,0,0,.15);
}

/* ─── GRID & CARDS ───────────────────────────────────── */
.grid-2 { display:grid; grid-template-columns:1.55fr 1fr; gap:22px; margin-bottom:22px; }
.grid-kpi { display:grid; grid-template-columns:repeat(4,1fr); gap:16px; margin-bottom:22px; }
.card {
  background:var(--card-bg); border-radius:14px;
  padding:20px 22px;
  box-shadow:0 2px 12px rgba(0,0,0,.06);
  border:1px solid var(--border);
}
.card h4 {
  font-size:0.93rem; font-weight:700;
  color:var(--primary-dk); margin-bottom:14px;
  display:flex; align-items:center; gap:8px;
}
.metric-card { border-left:5px solid var(--primary-lt); }
.metric-card h3 { font-size:0.7rem; color:var(--text-muted); text-transform:uppercase; letter-spacing:.8px; }
.metric-value { font-size:1.75rem; font-weight:800; color:var(--primary-dk); margin:4px 0; }
.metric-delta { font-size:0.73rem; font-weight:600; color:var(--primary-lt); }

/* ─── SAFETY ALERT ───────────────────────────────────── */
@keyframes slide-in { from{opacity:0;transform:translateY(-8px)} to{opacity:1;transform:translateY(0)} }
.safety-alert {
  border-radius:12px; padding:16px 18px;
  margin-bottom:18px;
  display:flex; align-items:flex-start; gap:14px;
  border-left:5px solid;
  box-shadow:0 2px 10px rgba(0,0,0,.07);
  animation:slide-in 0.35s ease;
}
.safety-alert.standard { background:#E8F4FD; border-color:#2196F3; color:#0C4375; }
.safety-alert.warning  { background:#FFF4E5; border-color:#FF9800; color:#6B3800; }
.safety-alert.critical { background:#FDECEA; border-color:#F44336; color:#6A1911; }
.safety-alert.extreme  { background:#1A0505; border-color:#FF0000; color:#FFD0CC; }
.safety-icon { font-size:1.75rem; line-height:1; }
.safety-text h5 { font-size:0.92rem; font-weight:800; margin-bottom:3px; }
.safety-text p  { font-size:0.81rem; line-height:1.5; }

/* ─── MAP ────────────────────────────────────────────── */
.map-container { height:300px; border-radius:10px; overflow:hidden; border:1px solid #D0C9B8; }

/* ─── CHAT ───────────────────────────────────────────── */
.chat-box {
  height:230px; overflow-y:auto;
  padding:12px; background:#FAFAF8;
  border-radius:10px; border:1px solid var(--border);
  margin-bottom:10px;
  display:flex; flex-direction:column; gap:10px;
}
.chat-row { display:flex; gap:8px; align-items:flex-end; }
.chat-row.driver { flex-direction:row-reverse; }
.chat-avatar {
  width:28px; height:28px; border-radius:50%;
  display:flex; align-items:center; justify-content:center;
  font-size:0.8rem; flex-shrink:0; background:#EAE6DE;
}
.chat-row.driver .chat-avatar { background:var(--primary); }
.chat-bubble {
  padding:8px 12px; border-radius:14px;
  font-size:0.82rem; line-height:1.5; max-width:82%;
}
.chat-row.corporate .chat-bubble { background:#EDEBE4; color:#2D3A1F; border-bottom-left-radius:4px; }
.chat-row.driver    .chat-bubble { background:var(--primary); color:#FFF; border-bottom-right-radius:4px; }
.chat-meta { font-size:0.62rem; color:#A09880; margin-top:2px; }
.chat-input-row { display:flex; gap:8px; }
.chat-input-row input {
  flex:1; padding:9px 13px; border-radius:8px;
  border:1px solid #C4BDAC; font-size:0.84rem; outline:none;
  font-family:"Inter",sans-serif;
  transition:border-color 0.2s;
}
.chat-input-row input:focus { border-color:var(--primary-lt); }
.chat-input-row button {
  padding:9px 16px; border-radius:8px; border:none;
  background:var(--primary-dk); color:#FFF;
  font-weight:700; cursor:pointer; white-space:nowrap;
  transition:background 0.2s;
}
.chat-input-row button:hover { background:var(--primary); }

/* ─── PROGRESS BAR ───────────────────────────────────── */
.prog-bar-track { background:#EAE6DE; border-radius:10px; height:10px; overflow:hidden; margin-bottom:10px; }
.prog-bar-fill  { background:linear-gradient(90deg,#4A7C2F,#2D5016); height:100%; transition:width .3s ease; }

/* ─── CONTROLS ───────────────────────────────────────── */
.controls-row { display:grid; grid-template-columns:repeat(4,1fr); gap:14px; margin-bottom:18px; }
.control-group label { display:block; font-size:0.77rem; font-weight:700; color:var(--primary-dk); margin-bottom:4px; }
.control-group select {
  width:100%; padding:8px 10px; border-radius:8px;
  border:1px solid #C4BDAC; font-weight:600; color:var(--primary-dk); outline:none;
  font-family:"Inter",sans-serif;
}

/* ─── TELEMETRY TABLE ────────────────────────────────── */
.tele-row { display:flex; justify-content:space-between; padding:8px 0; border-bottom:1px solid #F0EDE6; font-size:0.81rem; }
.tele-label { color:var(--text-muted); font-weight:600; }
.tele-val   { color:var(--primary-dk); font-weight:700; }

/* ─── AUDIO ADVISORY ─────────────────────────────────── */
.audio-box { background:#F0EDE6; padding:12px; border-radius:8px; border-left:3px solid var(--primary-lt); font-size:0.81rem; margin-bottom:12px; }
.play-btn {
  width:100%; padding:10px; border-radius:8px;
  border:none; background:var(--primary); color:#FFF;
  font-weight:700; cursor:pointer; transition:background 0.2s;
}
.play-btn:hover { background:var(--primary-dk); }

/* ─── FOOTER ─────────────────────────────────────────── */
.ieee-footer {
  background:linear-gradient(135deg,#111A06 0%,#1E2E0A 100%);
  border-radius:14px; padding:18px 26px; margin-top:28px;
  color:#A0B880; font-size:0.71rem;
  display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:14px;
}
.footer-title { color:var(--gold); font-weight:700; margin-bottom:4px; }
</style>
</head>
<body>

<div class="app-layout">

<!-- ═══════════════════════════════════════
     SIDEBAR
════════════════════════════════════════ -->
<aside class="sidebar">
  <div class="academic-card">
    <span class="ac-badge">🎓 Research Author</span>
    <h3 class="ac-name">Lokesh Kumar</h3>
    <p class="ac-id">Student ID: 2k22-SE-42</p>
    <hr class="ac-divider">
    <div class="ac-row">📧 2K22-SE-42@student.sau.edu.pk</div>
    <div class="ac-row">🏫 Sindh Agriculture University, Tandojam</div>
    <div class="ac-row">📄 Dept. of Software Engineering</div>
    <div class="ac-row" style="margin-top:8px;border-top:1px dashed #3A4F1A;padding-top:8px;color:var(--gold);">
      ⭐ Supervision &amp; Guidance:<br>Prof. Dr. Bhawani Shankar Chowdhry
    </div>
  </div>

  <!-- Route Selection -->
  <div class="route-toggle-section">
    <h4>🛣️ Route Selection</h4>
    <div class="route-btn-group">
      <div class="route-option active" id="r1-opt" onclick="selectRoute(1)">
        <span class="route-dot r1"></span>
        <div>
          <div class="route-option-label">Route 1 — Fastest</div>
          <div class="route-option-meta" id="r1-meta">162.5 km · ~3h 15m</div>
        </div>
      </div>
      <div class="route-option" id="r2-opt" onclick="selectRoute(2)">
        <span class="route-dot r2"></span>
        <div>
          <div class="route-option-label">Route 2 — Alternate</div>
          <div class="route-option-meta" id="r2-meta">Loading…</div>
        </div>
      </div>
    </div>
  </div>

  <!-- Fuel Cost Card -->
  <div class="fuel-card">
    <div class="fuel-label">⛽ Estimated Fuel Cost</div>
    <div class="fuel-value" id="sidebar-fuel">Rs. 5,718</div>
    <div class="fuel-note">@ Rs.282/L · 8 km/L · <span id="sidebar-dist">162.5</span> km</div>
  </div>

  <!-- Research Context -->
  <div class="sidebar-section">
    <h4>📋 Research Context</h4>
    <strong style="color:#C8D8A0;">Title:</strong><br>
    <em>Bridging the Digital Literacy Gap in Rural Agri-Logistics Using a Trilingual, Context-Aware IDAS</em>
    <br><br>
    <strong style="color:#C8D8A0;">Objective:</strong><br>
    Zero-literacy-barrier access to route safety for Sindhi, Urdu, and Dhatki drivers.
  </div>

  <div class="sidebar-section">
    <h4>⚙️ System Pipeline</h4>
    • Trilingual NLP Translation Layer<br>
    • OSRM True-Road Routing (1,313 pts)<br>
    • Dual Route: Fastest &amp; Alternate<br>
    • 4-Tier Context-Aware Safety Matrix<br>
    • gTTS Audio Advisory &amp; IoT Telemetry
  </div>
</aside>

<!-- ═══════════════════════════════════════
     MAIN CONTENT
════════════════════════════════════════ -->
<main class="main-content">
  <!-- Header -->
  <header class="app-header">
    <div>
      <h1>🌾 Agri-Logistics IDAS</h1>
      <p>Intelligent Driver Assistance System · Sindh Agricultural Supply Chain (Mithi → Hyderabad)</p>
    </div>
    <div style="text-align:right;">
      <span class="header-badge">PHASE 3 · FULL SYSTEM</span>
      <p style="font-size:0.7rem;color:var(--gold);margin-top:4px;">🌐 agri-idas.tech</p>
    </div>
  </header>

  <!-- Tab Bar -->
  <div class="tab-bar">
    <button class="tab-btn active" id="tab-corp-btn" onclick="switchTab('corp')">🏢 Corporate Dashboard</button>
    <button class="tab-btn"        id="tab-drv-btn"  onclick="switchTab('drv')">🚚 Driver Interface</button>
  </div>

  <!-- ════════════════════════════════
       TAB 1: CORPORATE DASHBOARD
  ════════════════════════════════ -->
  <div id="tab-corp">
    <div class="grid-kpi">
      <div class="card metric-card">
        <h3>Route Distance</h3>
        <div class="metric-value" id="kpi-dist">162.5 km</div>
        <div class="metric-delta" id="kpi-dist-delta">📍 Mithi → Hyderabad</div>
      </div>
      <div class="card metric-card">
        <h3>ETA Remaining</h3>
        <div class="metric-value" id="kpi-eta">3h 15m</div>
        <div class="metric-delta" id="kpi-eta-delta">▼ On Schedule</div>
      </div>
      <div class="card metric-card">
        <h3>Fuel Cost (PKR)</h3>
        <div class="metric-value" id="kpi-fuel">Rs. 5,718</div>
        <div class="metric-delta">@ Rs.282/L · 8 km/L</div>
      </div>
      <div class="card metric-card" style="border-left-color:#C62828;">
        <h3>Safety Score</h3>
        <div class="metric-value" id="kpi-safety" style="color:#C62828;">48%</div>
        <div class="metric-delta" id="kpi-safety-delta" style="color:#C62828;">▼ Rain + Night Risk</div>
      </div>
    </div>

    <div class="grid-2">
      <div class="card">
        <h4>🗺️ Live Fleet Map — Corporate View (CartoDB Positron)</h4>
        <div id="map-corp" class="map-container"></div>
      </div>
      <div class="card">
        <h4>💬 Dispatch Chat (English View)</h4>
        <div class="chat-box" id="corp-chat-box"></div>
        <form class="chat-input-row" onsubmit="sendCorpMessage(event)">
          <input type="text" id="corp-chat-input" placeholder="Message TRK-119 driver (English)…" autocomplete="off">
          <button type="submit">Send</button>
        </form>
      </div>
    </div>
  </div>

  <!-- ════════════════════════════════
       TAB 2: DRIVER INTERFACE
  ════════════════════════════════ -->
  <div id="tab-drv" style="display:none;">
    <!-- Simulation Controls -->
    <div class="controls-row">
      <div class="control-group">
        <label>🌐 Language</label>
        <select id="sel-lang" onchange="updateDriverContext()">
          <option value="Sindhi" selected>🌟 Sindhi</option>
          <option value="Urdu">🌙 Urdu</option>
          <option value="Dhatki">🌺 Dhatki</option>
          <option value="English">🌐 English</option>
        </select>
      </div>
      <div class="control-group">
        <label>📦 Cargo Type</label>
        <select id="sel-cargo" onchange="updateDriverContext()">
          <option value="Fragile" selected>🍅 Fragile / Tomatoes</option>
          <option value="Standard">📦 Standard</option>
          <option value="Cotton">🌿 Cotton</option>
          <option value="Wheat">🌾 Wheat</option>
        </select>
      </div>
      <div class="control-group">
        <label>⏱️ Time (Simulate)</label>
        <select id="sel-time" onchange="updateDriverContext()">
          <option value="Day">☀️ Day</option>
          <option value="Night" selected>🌙 Night</option>
        </select>
      </div>
      <div class="control-group">
        <label>☁️ Weather (Simulate)</label>
        <select id="sel-weather" onchange="updateDriverContext()">
          <option value="Clear">☀️ Clear</option>
          <option value="Rain" selected>🌧️ Rain</option>
        </select>
      </div>
    </div>

    <!-- Safety Alert -->
    <div id="safety-alert-panel" class="safety-alert extreme">
      <div class="safety-icon" id="alert-icon">⛔</div>
      <div class="safety-text">
        <h5 id="alert-title">INTEHAIYI KHATRO: Raat + Barish + Nazuk Maal</h5>
        <p id="alert-body">Teno khatarnak halat hik waqt gad thia aahin. Raftar 50% ghat karo. Hazard lights hinner chalao.</p>
      </div>
    </div>

    <!-- Route Progress -->
    <div class="card" style="margin-bottom:18px;">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
        <h4 style="margin:0;">🚗 Route Progress (Mithi → Hyderabad)</h4>
        <span id="prog-pct-badge" style="background:#4A7C2F;color:#FFF;font-size:0.73rem;font-weight:700;padding:3px 10px;border-radius:12px;">35% Completed</span>
      </div>
      <div class="prog-bar-track">
        <div class="prog-bar-fill" id="prog-bar-inner" style="width:35%;"></div>
      </div>
      <div style="display:flex;justify-content:space-between;font-size:0.77rem;color:#4A5C3A;font-weight:600;">
        <span id="prog-covered">📍 Covered: 56.9 / 162.5 km</span>
        <span id="prog-eta">⏱️ ETA Remaining: ~3h 15m</span>
      </div>
      <div style="margin-top:10px;">
        <input type="range" id="prog-slider" min="0" max="100" value="35"
          style="width:100%;accent-color:#4A7C2F;cursor:pointer;"
          oninput="updateProgress(this.value)">
      </div>
    </div>

    <!-- Driver Map + Chat -->
    <div class="grid-2">
      <div class="card">
        <h4>🧭 Navigation View — Driver (CartoDB Dark Matter)</h4>
        <div id="map-drv" class="map-container"></div>
      </div>
      <div class="card">
        <h4 id="drv-chat-title">💬 Dispatch Chat (🌟 Sindhi)</h4>
        <div class="chat-box" id="drv-chat-box"></div>
        <form class="chat-input-row" onsubmit="sendDrvMessage(event)">
          <input type="text" id="drv-chat-input" placeholder="Type in any language…" autocomplete="off">
          <button type="submit">Send</button>
        </form>
      </div>
    </div>

    <!-- Audio + Telemetry -->
    <div class="grid-2">
      <div class="card">
        <h4>🔊 Audio Advisory Guidance</h4>
        <div class="audio-box">
          <strong>Next Maneuver:</strong> Straight ahead on National Highway 8 for 45 km toward Matli.
        </div>
        <button class="play-btn" onclick="playAudioGuidance()">🔊 Play Advisory in Selected Language</button>
        <p id="audio-transcript" style="font-size:0.73rem;color:var(--text-muted);margin-top:8px;font-style:italic;"></p>
      </div>
      <div class="card">
        <h4>📡 IoT / WSN Vehicle Telemetry</h4>
        <div class="tele-row">
          <span class="tele-label">Current Speed</span>
          <span class="tele-val" id="tele-speed" style="color:#C62828;">42 km/h (Limit: 50)</span>
        </div>
        <div class="tele-row">
          <span class="tele-label">Road Surface</span>
          <span class="tele-val" id="tele-surface">🌧️ Wet / Slippery (μ=0.38)</span>
        </div>
        <div class="tele-row">
          <span class="tele-label">Cargo Temp / Hum</span>
          <span class="tele-val" id="tele-cargo">19.2°C (Controlled)</span>
        </div>
        <div class="tele-row">
          <span class="tele-label">GPS Location</span>
          <span class="tele-val" id="tele-gps" style="font-family:monospace;">24.9729°N, 69.2927°E</span>
        </div>
        <div class="tele-row" style="border:none;">
          <span class="tele-label">WSN Gateway</span>
          <span class="tele-val" style="color:#2E7D32;">🟢 Active (4G + LoRaWAN)</span>
        </div>
      </div>
    </div>
  </div>

  <!-- Footer -->
  <footer class="ieee-footer">
    <div>
      <div class="footer-title">📄 Research Citation</div>
      <div><em>Kumar, L.</em> (2024). "Bridging the Digital Literacy Gap in Rural Agri-Logistics." <em>Sindh Agriculture University Symposium.</em> Tandojam.</div>
    </div>
    <div style="text-align:right;">
      Agri-Logistics IDAS · Phase 3<br>
      <strong style="color:var(--gold);">© 2024 Lokesh Kumar</strong>
    </div>
  </footer>
</main>
</div>

<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script>
'use strict';

// ── ROAD-SNAPPED ROUTE COORDINATES (1,313 OSRM pts) ──────────────
const ROAD_COORDS = OSRM_PLACEHOLDER;

// ── STATE ─────────────────────────────────────────────────────────
const state = {
  messages: [{ role:'corporate', english:'🌾 Welcome TRK-119! Connected to IDAS Network. Safe travels on the Mithi → Hyderabad corridor.' }],
  progressPct: 35,
  lang: 'Sindhi',
  cargo: 'Fragile',
  time: 'Night',
  weather: 'Rain',
  activeRoute: 1,
  routeData: { r1: null, r2: null }
};

// ── FUEL CALCULATOR ───────────────────────────────────────────────
const FUEL_PKR = 282, FUEL_EFF = 8;
function calcFuelCost(km) { return Math.round((km / FUEL_EFF) * FUEL_PKR); }
function fmtPKR(n) { return 'Rs. ' + n.toLocaleString('en-PK'); }

// ── METRICS UPDATE ────────────────────────────────────────────────
function updateMetrics() {
  const rData = state.routeData['r' + state.activeRoute];
  const totalKm = rData ? parseFloat((rData.distance/1000).toFixed(1)) : 162.5;
  const covered = parseFloat((totalKm * state.progressPct / 100).toFixed(1));
  const remKm   = parseFloat((totalKm - covered).toFixed(1));

  let spd = 65;
  if (state.weather==='Rain' && state.time==='Night') spd = 42;
  else if (state.weather==='Rain' || state.time==='Night') spd = 55;
  const remMin = Math.round((remKm / spd) * 60);
  const hrs = Math.floor(remMin/60), mins = remMin % 60;

  let safety = 88;
  if (state.weather==='Rain') safety -= 22;
  if (state.time==='Night')   safety -= 18;
  if (state.cargo==='Fragile') safety -= 5;
  safety = Math.max(20, safety);

  const fuel = calcFuelCost(totalKm);
  const safetyColor = safety < 50 ? '#C62828' : safety < 70 ? '#E65100' : '#2E7D32';

  // KPI Cards
  el('kpi-dist').textContent  = totalKm + ' km';
  el('kpi-eta').textContent   = hrs + 'h ' + mins + 'm';
  el('kpi-fuel').textContent  = fmtPKR(fuel);
  el('kpi-safety').textContent = safety + '%';
  el('kpi-safety').style.color = safetyColor;
  el('kpi-safety-delta').textContent = safety < 50 ? '▼ Rain + Night Risk' : '▲ Conditions Normal';
  el('kpi-safety-delta').style.color = safetyColor;
  el('kpi-eta-delta').textContent = spd < 50 ? '▼ Slow — Adverse Conditions' : '▼ On Schedule';

  // Sidebar fuel
  el('sidebar-fuel').textContent = fmtPKR(fuel);
  el('sidebar-dist').textContent = totalKm;

  // Progress card
  const pct = state.progressPct;
  el('prog-bar-inner').style.width = pct + '%';
  el('prog-pct-badge').textContent = pct + '% Completed';
  el('prog-covered').textContent   = '📍 Covered: ' + covered + ' / ' + totalKm + ' km';
  el('prog-eta').textContent       = '⏱️ ETA Remaining: ~' + hrs + 'h ' + mins + 'm';

  // Telemetry
  el('tele-speed').textContent = spd + ' km/h (Limit: ' + (spd < 50 ? '50' : '60') + ')';
  el('tele-speed').style.color = spd < 50 ? '#C62828' : '#2E7D32';
  el('tele-surface').textContent = state.weather === 'Rain' ? '🌧️ Wet / Slippery (μ=0.38)' : '✅ Dry (μ=0.72)';

  // Route meta in sidebar
  if (state.routeData.r1) {
    const d = (state.routeData.r1.distance/1000).toFixed(0);
    const t = Math.round(state.routeData.r1.duration/60);
    el('r1-meta').textContent = d + ' km · ~' + t + 'm';
  }
  if (state.routeData.r2) {
    const d = (state.routeData.r2.distance/1000).toFixed(0);
    const t = Math.round(state.routeData.r2.duration/60);
    el('r2-meta').textContent = d + ' km · ~' + t + 'm';
  }

  updateSafetyAlert();
}

// ── SAFETY ALERT ──────────────────────────────────────────────────
const SAFETY_TEXTS = {
  extreme: {
    cls:'extreme', icon:'⛔',
    en:'EXTREME RISK: Night + Rain + Fragile Cargo — Reduce speed 50%. Hazard lights ON.',
    sd:'INTEHAIYI KHATRO: Raat + Barish + Nazuk Maal — Raftar 50% ghat karo. Hazard lights hinner chalao.',
    ur:'ANTEHAI KHATARNAK: Raat + Baarish + Nazuk Maal — Raftar 50% ghatayein.',
    dh:'BAHUT KHATRO: Raat + Barish + Nazuk Maal — Raftar 50% ghat karo.'
  },
  critical: {
    cls:'critical', icon:'🛑',
    en:'CRITICAL: Rain on Highway — Slippery road (μ=0.38). Speed limit 60 km/h.',
    sd:'KHATARNAK: Highway te barish — Sadak chikani ahe. Raftar 60 km/h.',
    ur:'KHATARNAK: Highway par baarish — Sadak phislan wali. Raftar 60 km/h.',
    dh:'KHATARNAK: Barish waro raah — Sadak chikani. Raftar 60 km/h.'
  },
  warning: {
    cls:'warning', icon:'⚠️',
    en:'WARNING: Night driving — Reduce speed to 60 km/h. High-beam headlights ON.',
    sd:'KHABARDAR: Raat driving — Raftar 60 km/h. Headlights tez chalao.',
    ur:'KHABARDAR: Raat gaari — Raftar 60 km/h. Headlights tez rakhein.',
    dh:'KHABARDAR: Raat driving — Raftar 60 km/h. Headlights tez karo.'
  },
  standard: {
    cls:'standard', icon:'ℹ️',
    en:'STANDARD CONDITIONS: Road clear. Maintain speed limit. Drive safe!',
    sd:'MAMULI HALAT: Rasto saaf ahe. Speed limit manno. Salaamti halo!',
    ur:'MAMULI HALAT: Rasta saaf hai. Speed limit manein. Salamti se chalein!',
    dh:'MAMULI HALAT: Raah saaf hai. Raftar limit manno. Salaamti vanj!'
  }
};
function updateSafetyAlert() {
  let key = 'standard';
  if (state.weather==='Rain' && state.time==='Night') key='extreme';
  else if (state.weather==='Rain') key='critical';
  else if (state.time==='Night') key='warning';

  const t = SAFETY_TEXTS[key];
  const langKey = {Sindhi:'sd', Urdu:'ur', Dhatki:'dh', English:'en'}[state.lang] || 'en';

  el('safety-alert-panel').className = 'safety-alert ' + t.cls;
  el('alert-icon').textContent  = t.icon;
  el('alert-title').textContent = t[langKey];
  el('alert-body').textContent  = ''; // condensed for mobile
}

// ── MAPS ──────────────────────────────────────────────────────────
let mapCorp, mapDrv;
let polyR1Corp, polyR1Drv, polyR2Corp, polyR2Drv;

function initMaps() {
  const CORP_TILE = 'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png';
  const DRV_TILE  = 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png';
  const ATTR = '&copy; <a href="https://carto.com/">CARTO</a> &copy; <a href="https://openstreetmap.org/">OSM</a>';

  mapCorp = L.map('map-corp').setView([25.07,69.10],8);
  L.tileLayer(CORP_TILE,{attribution:ATTR,maxZoom:19,subdomains:'abcd'}).addTo(mapCorp);

  mapDrv = L.map('map-drv').setView([25.07,69.10],8);
  L.tileLayer(DRV_TILE,{attribution:ATTR,maxZoom:19,subdomains:'abcd'}).addTo(mapDrv);

  // Custom markers
  const iconGreen = L.divIcon({html:'<div style="width:12px;height:12px;background:#4A7C2F;border-radius:50%;border:2px solid #fff;box-shadow:0 0 8px rgba(74,124,47,.8)"></div>',iconAnchor:[6,6],className:''});
  const iconRed   = L.divIcon({html:'<div style="width:12px;height:12px;background:#C62828;border-radius:50%;border:2px solid #fff;box-shadow:0 0 8px rgba(198,40,40,.8)"></div>',iconAnchor:[6,6],className:''});

  L.marker([24.7437,69.7961],{icon:iconGreen}).addTo(mapCorp).bindPopup('<b>Mithi</b> — Departure');
  L.marker([25.3960,68.3578],{icon:iconRed  }).addTo(mapCorp).bindPopup('<b>Hyderabad</b> — Destination');
  L.marker([24.7437,69.7961],{icon:iconGreen}).addTo(mapDrv).bindPopup('<b>Mithi</b> — Departure');
  L.marker([25.3960,68.3578],{icon:iconRed  }).addTo(mapDrv).bindPopup('<b>Hyderabad</b> — Destination');

  // Draw embedded 1,313-point road-snapped route immediately
  polyR1Corp = L.polyline(ROAD_COORDS,{color:'#2D5016',weight:6,opacity:.9}).addTo(mapCorp);
  polyR1Drv  = L.polyline(ROAD_COORDS,{color:'#4A7C2F',weight:6,opacity:.9}).addTo(mapDrv);

  setTimeout(() => { mapCorp.invalidateSize(); mapDrv.invalidateSize(); }, 200);

  // Async: fetch live OSRM to refine + get Route 2
  loadDualRoutes();
}

async function loadDualRoutes() {
  const WP = '69.7961,24.7436;68.8893,24.9390;68.3578,25.3960';
  const WP2= '69.7961,24.7436;69.2760,24.9730;68.9070,25.1030;68.5000,25.3000;68.3578,25.3960';
  try {
    const [r1,r2] = await Promise.all([
      fetch('https://router.project-osrm.org/route/v1/driving/'+WP+'?overview=full&geometries=geojson').then(r=>r.json()),
      fetch('https://router.project-osrm.org/route/v1/driving/'+WP2+'?overview=full&geometries=geojson').then(r=>r.json())
    ]);
    if (r1.routes?.[0]) {
      const c1 = r1.routes[0].geometry.coordinates.map(c=>[c[1],c[0]]);
      state.routeData.r1 = {distance:r1.routes[0].distance, duration:r1.routes[0].duration, coords:c1};
      polyR1Corp.setLatLngs(c1);
      polyR1Drv.setLatLngs(c1);
    }
    if (r2.routes?.[0]) {
      const c2 = r2.routes[0].geometry.coordinates.map(c=>[c[1],c[0]]);
      state.routeData.r2 = {distance:r2.routes[0].distance, duration:r2.routes[0].duration, coords:c2};
      polyR2Corp = L.polyline(c2,{color:'#3B82F6',weight:4,opacity:.6,dashArray:'8 5'});
      polyR2Drv  = L.polyline(c2,{color:'#60A5FA',weight:4,opacity:.6,dashArray:'8 5'});
    }
    updateMetrics();
  } catch(e) {
    console.warn('OSRM offline — using 1,313 embedded road-centerline points.',e.message);
    updateMetrics();
  }
}

function selectRoute(n) {
  state.activeRoute = n;
  el('r1-opt').className = 'route-option' + (n===1?' active':'');
  el('r2-opt').className = 'route-option' + (n===2?' active':'');

  [polyR1Corp,polyR1Drv,polyR2Corp,polyR2Drv].forEach(p=>p&&p.remove&&p.remove());

  if (n===1) {
    polyR1Corp && polyR1Corp.addTo(mapCorp);
    polyR1Drv  && polyR1Drv.addTo(mapDrv);
    if (polyR2Corp) { polyR2Corp.setStyle({opacity:.25}); polyR2Corp.addTo(mapCorp); }
    if (polyR2Drv)  { polyR2Drv.setStyle({opacity:.25});  polyR2Drv.addTo(mapDrv); }
  } else {
    if (!state.routeData.r2) { alert('Alternate route still loading. Please wait a moment.'); selectRoute(1); return; }
    polyR2Corp && polyR2Corp.setStyle({color:'#3B82F6',weight:5,opacity:.9,dashArray:''});
    polyR2Drv  && polyR2Drv.setStyle({color:'#60A5FA',weight:5,opacity:.9,dashArray:''});
    polyR2Corp && polyR2Corp.addTo(mapCorp);
    polyR2Drv  && polyR2Drv.addTo(mapDrv);
    if (polyR1Corp) { polyR1Corp.setStyle({opacity:.2}); polyR1Corp.addTo(mapCorp); }
    if (polyR1Drv)  { polyR1Drv.setStyle({opacity:.2});  polyR1Drv.addTo(mapDrv); }
  }
  updateMetrics();
}

// ── TAB SWITCH ────────────────────────────────────────────────────
function switchTab(tab) {
  el('tab-corp').style.display = tab==='corp' ? 'block' : 'none';
  el('tab-drv').style.display  = tab==='drv'  ? 'block' : 'none';
  el('tab-corp-btn').className = 'tab-btn' + (tab==='corp'?' active':'');
  el('tab-drv-btn').className  = 'tab-btn' + (tab==='drv'?' active':'');
  setTimeout(()=>{mapCorp&&mapCorp.invalidateSize();mapDrv&&mapDrv.invalidateSize();},150);
}

// ── SIMULATION CONTROLS ───────────────────────────────────────────
function updateProgress(val) { state.progressPct=parseInt(val); updateMetrics(); }
function updateDriverContext() {
  state.lang    = el('sel-lang').value;
  state.cargo   = el('sel-cargo').value;
  state.time    = el('sel-time').value;
  state.weather = el('sel-weather').value;
  el('drv-chat-title').textContent = '💬 Dispatch Chat (' + state.lang + ')';
  updateMetrics();
  renderChat();
}

// ── SMART NLP ENGINE ──────────────────────────────────────────────
function safeReply(obj) {
  try {
    return obj[state.lang] || obj['Urdu'] || obj['English'] || '📡 IDAS: Message received.';
  } catch(e) {
    return '📡 IDAS: Network reconnecting… Please try again.';
  }
}

function generateSmartReply(userText) {
  const v   = (userText||'').toLowerCase().trim();
  const rD  = state.routeData['r'+state.activeRoute];
  const tot = rD ? parseFloat((rD.distance/1000).toFixed(1)) : 162.5;
  const cov = parseFloat((tot * state.progressPct/100).toFixed(1));
  const rem = parseFloat((tot - cov).toFixed(1));
  let avgSpd = 65;
  if (state.weather==='Rain' && state.time==='Night') avgSpd=42;
  else if (state.weather==='Rain'||state.time==='Night') avgSpd=55;
  const remMin = Math.round((rem/avgSpd)*60);
  const hrs = Math.floor(remMin/60), mins = remMin%60;
  const spd = avgSpd+' km/h';
  const fuelLeft = fmtPKR(calcFuelCost(rem));

  if (/route|rasto|raah|give|where|path|map|destination|way|kahan|location|mera/i.test(v)) return {
    Sindhi:  '🗺️ RASTO: Mithi → Hyderabad ('+tot+' km), Route '+state.activeRoute+'. Maujuda jagah: '+cov+' km Digri wath. '+rem+' km baaki. ETA: '+hrs+'h '+mins+'m.',
    Urdu:    '🗺️ RASTA: Mithi → Hyderabad ('+tot+' km), Route '+state.activeRoute+'. Maujuda maqam: '+cov+' km Digri ke paas. '+rem+' km baaqi. ETA: '+hrs+'h '+mins+'m.',
    Dhatki:  '🗺️ RAAH: Mithi → Hyderabad ('+tot+' km). '+cov+' km Digri paas pura. '+rem+' km baaki.',
    English: '🗺️ ROUTE [R'+state.activeRoute+']: Mithi → Hyderabad ('+tot+' km). Covered: '+cov+' km near Digri. Remaining: '+rem+' km. ETA: '+hrs+'h '+mins+'m.'
  };
  if (/mura|muri|side|direction|kayi|turn|left|right|khabbe|saje|modh/i.test(v)) return {
    Sindhi:  '🧭 DIRECTION: National Highway 8 te siddho vanj 45 km tak. Naukot junction te seedha — Matli taraf.',
    Urdu:    '🧭 DIRECTION: Agle 45 km seedha National Highway 8 par. Naukot junction par seedhe rahein.',
    Dhatki:  '🧭 DIRECTION: NH-8 te siddha vanj 45 km. Naukot junction te seedha raho.',
    English: '🧭 DIRECTION: Continue straight on National Highway 8 for 45 km. No turn at Naukot — head toward Matli.'
  };
  if (/speed|fast|slow|raftar|tez|limit|chalo/i.test(v)) return {
    Sindhi:  '⚡ RAFTAR: '+spd+' ('+state.weather+' mosam, '+state.time+'). Achanak brake na kayo.',
    Urdu:    '⚡ RAFTAR: '+spd+' ('+state.weather+' mausam, '+state.time+'). Mehfooz fasla rakhein.',
    Dhatki:  '⚡ RAFTAR: '+spd+'. Tezi na karo.',
    English: '⚡ SPEED: Recommended '+spd+' — '+state.weather+' weather, '+state.time+' conditions. Maintain 6-second gap.'
  };
  if (/time|eta|distance|km|duration|pohchan|when|reach|ghante/i.test(v)) return {
    Sindhi:  '⏱️ ETA: '+hrs+'h '+mins+'m baaki. '+rem+' km. Fuel: '+fuelLeft+'.',
    Urdu:    '⏱️ ETA: '+hrs+' ghante '+mins+' min baaqi. '+rem+' km. Fuel: '+fuelLeft+'.',
    Dhatki:  '⏱️ ETA: '+hrs+'h '+mins+'m baaki. '+rem+' km baaki.',
    English: '⏱️ ETA: ~'+hrs+'h '+mins+'m to Hyderabad. Distance left: '+rem+' km. Fuel cost remaining: '+fuelLeft+'.'
  };
  if (/fuel|petrol|gas|cost|kharcha|paisa|rupay|pump/i.test(v)) return {
    Sindhi:  '⛽ PETROL: Baaki safar kharcha: '+fuelLeft+'. Aglo pump: Naukot (~18 km).',
    Urdu:    '⛽ PETROL: Baaki kharcha: '+fuelLeft+'. Agla pump: Naukot (~18 km).',
    Dhatki:  '⛽ PETROL: Baaki kharcha: '+fuelLeft+'. Aglo pump: Naukot.',
    English: '⛽ FUEL COST: Remaining route cost: '+fuelLeft+' ('+rem+' km ÷ 8 km/L × Rs.282). Next station: Naukot (~18 km).'
  };
  if (/maal|tamatar|cargo|load|gadi|tomato|produce|fragile/i.test(v)) return {
    Sindhi:  '🍅 MAAL: '+state.cargo+'. Temp: 19.2°C ✅. Achanak brake na kayo.',
    Urdu:    '🍅 MAAL: '+state.cargo+'. Temp: 19.2°C ✅. Achanak brake mat lagayein.',
    Dhatki:  '🍅 MAAL: '+state.cargo+'. Temp: 19.2°C. Achanak brake na karo.',
    English: '🍅 CARGO: '+state.cargo+' loaded. Temp: 19.2°C ✅. Avoid harsh braking.'
  };
  if (/weather|rain|barish|mosam|night|raat|dark|slippery/i.test(v)) return {
    Sindhi:  '🌧️ MOSAM: '+state.weather+' ('+state.time+'). Sadak chikani (μ=0.38). Hazard lights on.',
    Urdu:    '🌧️ MAUSAM: '+state.weather+' ('+state.time+'). Sadak phislan wali. Hazard lights on.',
    Dhatki:  '🌧️ MOSAM: '+state.weather+'. Sadak chikani. Hazard lights on.',
    English: '🌧️ WEATHER: '+state.weather+', '+state.time+'. Road friction μ=0.38. Stopping distance 2×. Hazard lights ON.'
  };
  if (/hello|hi|salam|aayo|kiin|kean|welcome|khush/i.test(v)) return {
    Sindhi:  '👋 IDAS: Khush aayo TRK-119! Route '+state.activeRoute+' active. '+state.progressPct+'% mukammal. Kihn madad kayo?',
    Urdu:    '👋 IDAS: Khush aamdeed TRK-119! Route '+state.activeRoute+' active. '+state.progressPct+'% mukammal. Kaise madad karein?',
    Dhatki:  '👋 IDAS: Aavkaari TRK-119! Route '+state.activeRoute+'. Kihn madad karo?',
    English: '👋 IDAS: Welcome TRK-119! Route '+state.activeRoute+' active — '+state.progressPct+'% complete. How can dispatch assist?'
  };
  if (/kharab|breakdown|help|madad|emergency|accident|jam|janwar|hazard|khatro|stuck/i.test(v)) return {
    Sindhi:  '🚨 HIGH ALERT: TRK-119 '+cov+' km wath khatro. Diplo rasto nayo alert. Naukot Police Post (~12 km).',
    Urdu:    '🚨 HIGH ALERT: TRK-119 '+cov+' km par hazard. Diplo se alternate rasta. Naukot Police (~12 km).',
    Dhatki:  '🚨 HIGH ALERT: TRK-119 '+cov+' km paas khatro. Diplo raah. Saabit raho.',
    English: '🚨 HIGH ALERT: Hazard logged at '+cov+' km (TRK-119). Alternate via Diplo computed. Naukot Police Post ~12 km. Stay calm.'
  };
  // Dynamic fallback
  return {
    Sindhi:  '📡 DISPATCH: TRK-119 paighaam record. Route '+state.activeRoute+' — '+cov+' km ('+state.progressPct+'%). Raftar: '+spd+'. ETA: '+hrs+'h '+mins+'m.',
    Urdu:    '📡 DISPATCH: TRK-119 paigham record. Route '+state.activeRoute+' — '+cov+' km ('+state.progressPct+'%). Raftar: '+spd+'. ETA: '+hrs+'h '+mins+'m.',
    Dhatki:  '📡 DISPATCH: TRK-119 sandesh record. '+cov+' km ('+state.progressPct+'%). Raftar: '+spd+'.',
    English: '📡 DISPATCH: Message logged for TRK-119. Route '+state.activeRoute+' — '+cov+' km of '+tot+' km ('+state.progressPct+'%). Speed: '+spd+'. ETA: '+hrs+'h '+mins+'m. Fuel left: '+fuelLeft+'.'
  };
}

// ── CHAT RENDER ───────────────────────────────────────────────────
function renderChat() {
  ['corp','drv'].forEach(who => {
    const box = el(who+'-chat-box');
    let html = '';
    state.messages.forEach(msg => {
      const isDrv = msg.role === 'driver';
      let text;
      if (who === 'corp') text = isDrv ? msg.original : msg.english;
      else text = isDrv ? msg.original : safeReply(msg.replyObj||{English:msg.english,Sindhi:msg.english,Urdu:msg.english,Dhatki:msg.english});
      html += `<div class="chat-row ${isDrv?'driver':'corporate'}">
        <div class="chat-avatar">${isDrv?'🚚':'🏢'}</div>
        <div>
          <div class="chat-bubble">${text}</div>
          <div class="chat-meta">${isDrv?(who==='corp'?'🌐 '+state.lang+' → EN':'You ('+state.lang+')'):(who==='corp'?'🏢 Dispatch EN':'🏢 → '+state.lang)}</div>
        </div></div>`;
    });
    box.innerHTML = html || '<div style="text-align:center;color:#9CA3AF;font-size:0.78rem;padding:20px;">No messages yet.</div>';
    box.scrollTop = box.scrollHeight;
  });
}

function sendDrvMessage(e) {
  e.preventDefault();
  const inp = el('drv-chat-input'), val = inp.value.trim();
  if (!val) return;
  const replyObj = generateSmartReply(val);
  const isHazard = /kharab|breakdown|help|madad|emergency|accident|hazard|khatro/i.test(val);
  state.messages.push({role:'driver', original:(isHazard?'🚨 ':'')+val, english:(isHazard?'🚨 HAZARD: ':'')+val});
  state.messages.push({role:'corporate', english:replyObj.English||replyObj.Sindhi, replyObj});
  inp.value=''; renderChat();
}

function sendCorpMessage(e) {
  e.preventDefault();
  const inp = el('corp-chat-input'), val = inp.value.trim();
  if (!val) return;
  const reply = {
    English:'✅ Advisory received by TRK-119. Driver notified in '+state.lang+'.',
    Sindhi: '✅ Advisory TRK-119 khe mili. '+state.lang+' mein.',
    Urdu:   '✅ Advisory TRK-119 ko mili. '+state.lang+' mein.',
    Dhatki: '✅ Advisory TRK-119 khe mili.'
  };
  state.messages.push({role:'corporate', english:'🏢 DISPATCH: '+val, replyObj:{English:'🏢 DISPATCH: '+val,Sindhi:'🏢 DISPATCH: '+val,Urdu:'🏢 DISPATCH: '+val,Dhatki:'🏢 DISPATCH: '+val}});
  state.messages.push({role:'driver', original:safeReply(reply), english:reply.English});
  inp.value=''; renderChat();
}

// ── AUDIO ─────────────────────────────────────────────────────────
function playAudioGuidance() {
  if (!window.speechSynthesis) return;
  window.speechSynthesis.cancel();
  const langMap = {Sindhi:'ur-PK', Urdu:'ur-PK', Dhatki:'ur-PK', English:'en-US'};
  const msgs = {
    Sindhi:  'IDAS Alert TRK-119 laye. National Highway 8 te barish. Raftar ghat karo. Salaamti saan halo.',
    Urdu:    'IDAS Alert Truck 119. National Highway 8 par baarish. Raftar ghatayein. Salamti se chalein.',
    Dhatki:  'IDAS Alert TRK-119. NH-8 te barish. Raftar ghat karo. aaram sa jao.',
    English: 'IDAS Alert for Truck 119. Rain on National Highway 8. Reduce speed. Drive safely.'
  };
  const utt = new SpeechSynthesisUtterance(msgs[state.lang]||msgs.English);
  utt.lang = langMap[state.lang]||'en-US'; utt.rate=0.88; utt.pitch=1.0;
  window.speechSynthesis.speak(utt);
  el('audio-transcript').textContent = '🔊 Playing: ' + (msgs[state.lang]||msgs.English);
}

// ── HELPERS ───────────────────────────────────────────────────────
function el(id) { return document.getElementById(id); }

// ── BOOT ──────────────────────────────────────────────────────────
window.addEventListener('DOMContentLoaded', () => {
  initMaps();
  updateMetrics();
  renderChat();
});
window.addEventListener('resize', () => {
  setTimeout(()=>{ mapCorp&&mapCorp.invalidateSize(); mapDrv&&mapDrv.invalidateSize(); },200);
});
</script>
</body>
</html>'''

# Inject the 1,313-point coordinate array
HTML = HTML.replace('OSRM_PLACEHOLDER', OSRM_COORDS)

with open('index.html','w',encoding='utf-8') as f:
    f.write(HTML)

print(f'SUCCESS — index.html written: {len(HTML):,} bytes, {HTML.count(chr(10))} lines')
