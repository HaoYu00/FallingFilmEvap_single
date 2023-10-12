def limitation():
    dict_limi = {
        '1':"Max number of pass: 2",
        '2':"Uniform liquid distribution",
        '3':"fluid is mixed at the outlet of the passes (tube side liquid, shell side liquid, shell side vapor)",
        '4':"no imposed vapor",
        '5':"tube array is rectanguler",
        '6':"liquid level effect is not considered",
        '7':"vapor exhauster is installed at the top of the evaporator top"
    }
    print("limitaiton of this program:")
    for key, value in dict_limi.items():
        print('    ', key, ' : ', value)
    print("---------------------------")
def citation():
    citation_ = "Hao-YuLin, M Muneeshwaran, Cheng-Min Yang, Kashif Nawaz, Chi-Chuan Wang, 'On Falling Film Evaporator - A Review of Mechanisms and Critical Assessment of Correlation on a Horizontal Tube Bundle With Updated Development', International Communications On Heat & Mass Transfer, 2023"
    # print(citation_)
    return citation_
# limitation()