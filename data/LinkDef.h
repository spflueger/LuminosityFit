#ifdef __CINT__

#pragma link off all globals;
#pragma link off all classes;
#pragma link off all functions;

#pragma link C++ class LumiFit::LmdDimensionOptions+;
#pragma link C++ class LumiFit::LmdDimension+;

#pragma link C++ class std::set < LumiFit::LmdDimension >+;

#pragma link C++ class PndLmdElasticDataBundle+;
#pragma link C++ class PndLmdFitDataBundle+;
#pragma link C++ class PndLmdAbstractData+;
#pragma link C++ class PndLmdHistogramData+;
#pragma link C++ class PndLmdAngularData+;
#pragma link C++ class PndLmdAcceptance+;

#pragma link C++ class std::vector < PndLmdAngularData >+;
#pragma link C++ class std::vector < PndLmdAcceptance >+;
#pragma link C++ class std::vector < PndLmdHistogramData >+;

#endif
