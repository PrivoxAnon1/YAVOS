var CFG_YAML = '';
var RADIO_VALUE_NAMES = ['STT', 'TTS', 'MsgBus', 'AudioInBus', 'AudioOutBus'];
var CHECKBOX_VALUE_NAMES = ['MicLocal', 'MicRemote', 'LocalSPKR', 'RemoteSPKR', 'BargeIn', 'STTUseGPU'];
var SELECT_VALUE_NAMES = ['MicVad', 'STTModel', 'STTService', 'TTSVoice', 'TTSService', 'LogLevel'];
var TEXT_VALUE_NAMES = ['MsgBusPort', 'AudioInPort', 'AudioOutPort', 'MinConf', 'STTKey', 'TTSKey', 'MicLevelCmd', 'SpkrLevelCmd', 'PlayWavCmd', 'RecordWavCmd', 'FfmpegCmd'];
var AVAILABLE_SKILLS = [];
var INSTALLED_SKILLS = [];
var ALL_SKILLS = [];
var DRIVERS = [];
var LAST_LOCAL_TTS_SVC = '';
var LAST_LOCAL_TTS_MODEL = '';
var LAST_REMOTE_TTS_SVC = '';
var LAST_REMOTE_TTS_MODEL = '';
var LAST_LOCAL_STT_SVC = '';
var LAST_LOCAL_STT_MODEL = '';
var LAST_REMOTE_STT_SVC = '';
var LAST_REMOTE_STT_MODEL = '';

function setSkills(allSkills){
  // now that we have all the available skills we can grab the ones currently installed
  ALL_SKILLS = allSkills;
  try {
    loadYamlFile();
  } catch (error) {
    console.log("Warning yavos.yml not present");
  }
}

// get skills file
function loadSkillsFile(){
  const rstr = getRandomArbitrary(1, 65535); 
  fetch('/local_store/default_skills.json?cache_key=' + rstr) 
  .then(response => {
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return response.json(); 
  })
  .then(data => {
    setSkills(data);
  })
  .catch(error => {
    console.error('Error fetching file default skills:', error);
  });
}

function renderAvailableSkills(){
  let skillHtml = '';
  for(let indx=0;indx < AVAILABLE_SKILLS.length;indx++){
    skillHtml += `<span class='dblClass' ondblclick="dblClicked(0, this);">${AVAILABLE_SKILLS[indx]}</span><br/>`;
  }
  document.getElementById('available_skills').innerHTML = skillHtml;
}

function renderInstalledSkills(){
  let skillHtml = '';
  for(let indx=0;indx < INSTALLED_SKILLS.length;indx++){
    skillHtml += `<span class='dblClass' ondblclick="dblClicked(1, this);">${INSTALLED_SKILLS[indx]}</span><br/>`;
  }
  document.getElementById('installed_skills').innerHTML = skillHtml;
}

function renderSkills(){
  //renderInstalledSkills();
  //renderAvailableSkills();
}

function dblClicked(which, what){
  // which is either 0 for available or 1 for installed
  // inner html is the value of this option
  let skillName = what.innerHTML;
  if (which == 0){
    let index = AVAILABLE_SKILLS.indexOf(skillName);
    AVAILABLE_SKILLS.splice(index, 1); // Removes 1 element starting from 'index'
    INSTALLED_SKILLS.push(skillName);
  } else {
    let index = INSTALLED_SKILLS.indexOf(skillName);
    INSTALLED_SKILLS.splice(index, 1); // Removes 1 element starting from 'index'
    AVAILABLE_SKILLS.push(skillName);
  }
  renderSkills();
}

function getRadioOptionValue(domName){
  let thisButton = '';
  const radioButtons = document.getElementsByName(domName);
  for(let x=0;x < radioButtons.length;x++){
    thisButton = radioButtons[x];
    if (thisButton.checked){
        return(thisButton.id);
    }
  }
}

function setRadioOption(domName, valueToSelect) {
  const radioButtons = document.getElementsByName(domName);
  radioButtons.forEach(radio => {
    if (radio.value === valueToSelect) {
      radio.checked = true; 
    } else {
      radio.checked = false; 
    }
  });
}

function setSelectOption(domName, valueToSelect) {
  valueToSelect = valueToSelect.trim().replaceAll("'","");
  const selectOptions = document.getElementsByName(domName)[0].options;
  for(let indx=0;indx < selectOptions.length;indx++){
    if (selectOptions[indx].value === valueToSelect) {
      selectOptions[indx].selected = true; 
      selectOptions.selectedIndex = indx;
    } else {
      selectOptions[indx].selected = false; 
    }
  }
}

function handleSttWhereChange(which){
  let sttModel = document.getElementById("STTModel").value;
  let sttService = document.getElementById("STTService").value;
  let sttWhich = getRadioOptionValue("STT");
  if (sttWhich == 'remote'){
	  LAST_LOCAL_STT_MODEL = sttModel;
	  LAST_LOCAL_STT_SVC = sttService;
  } else {
	  LAST_REMOTE_STT_MODEL = sttModel;
	  LAST_REMOTE_STT_SVC = sttService;
  }
  updateDrivers();
  return(true);
}

function handleTtsWhereChange(which){
  let ttsModel = document.getElementById("TTSVoice").value;
  let ttsService = document.getElementById("TTSService").value;
  let ttsWhich = getRadioOptionValue("TTS");
  if (ttsWhich == 'remote'){
	  LAST_LOCAL_TTS_MODEL = ttsModel;
	  LAST_LOCAL_TTS_SVC = ttsService;
  } else {
	  LAST_REMOTE_TTS_MODEL = ttsModel;
	  LAST_REMOTE_TTS_SVC = ttsService;
  }
  updateDrivers();
  return(false);
}

function handleMicWhereChange(which){
  let localOptions = `<option>PriVoice Local</option><option>Custom</option>`;
  let remoteOptions = `<option>PriVoice Remote</option><option>Custom</option>`;
  let selectHTML = `<select id=mic_service>`;
  if (which == 'remote'){
    selectHTML += remoteOptions;
  } else {
    selectHTML += localOptions;
  }
  selectHTML += "</select>";
  document.getElementById('mic_where_select').innerHTML = selectHTML;
}

function getCfgVal(valName){
  for (let indx=0;indx < CFG_YAML.length;indx++){
    let line = CFG_YAML[indx].trim();
    let la = line.split(":");
    let yName = la[0].trim();
    if (yName == valName){
      let yVal = la[1].replaceAll("'", "").trim();
      return(yVal);
    }
  }
  return(null);
}

function getSkillsFromYaml(){
  for (let indx=0;indx < CFG_YAML.length;indx++){
    let line = CFG_YAML[indx].trim();
    if (line[0] == '-'){
      INSTALLED_SKILLS.push( line.slice(2) );
    }
  }
}

function setDomFromYaml(data){
  CFG_YAML = data.split("\n");

  for(let x=0;x < TEXT_VALUE_NAMES.length;x++){
    let domName = TEXT_VALUE_NAMES[x];

    try {
      document.getElementById(domName).value = getCfgVal(domName);
    } catch (error) {
      console.log("Warning Text domId not present " + domName);
    }
  }

  for(let x=0;x < RADIO_VALUE_NAMES.length;x++){
    let domName = RADIO_VALUE_NAMES[x];
    let domElement = document.getElementsByName(domName)[0];
    try {
      domElement.value = getCfgVal(domName);
      setRadioOption(domName, getCfgVal(domName));
    } catch (error) {
      console.log("Warning Radio domId not present " + domName);
    }
  }

  for(let x=0;x < SELECT_VALUE_NAMES.length;x++){
    let domName = SELECT_VALUE_NAMES[x];
    let domElement = document.getElementsByName(domName)[0];
    try {
      domElement.value = getCfgVal(domName);
      setSelectOption(domName, getCfgVal(domName));
    } catch (error) {
      console.log("Warning Select domId not present " + domName);
    }
  }

  for(let x=0;x < CHECKBOX_VALUE_NAMES.length;x++){
    let domName = CHECKBOX_VALUE_NAMES[x];
    let curVal = document.getElementById(domName).checked;
    let newVal = getCfgVal(domName);
    if (curVal.toString() != newVal){
      document.getElementById(domName).click();
    }
  }

  // process skills
  getSkillsFromYaml();

  for(skill in ALL_SKILLS){
    let thisSkill = ALL_SKILLS[skill];
    if (INSTALLED_SKILLS.indexOf(thisSkill['skill_name']) == -1){
      AVAILABLE_SKILLS.push( thisSkill['skill_name'] );
    }
  }
  renderSkills();
}

function getRandomArbitrary(min, max) {
  let rn = Math.random() * (max - min) + min;
  rn = rn.toString().replace(".","");
  return rn;
}

// get yaml file
function loadYamlFile(){
  const rstr = getRandomArbitrary(1, 65535); 
  fetch('/yavos.yml?cachekey=' + rstr) 
  .then(response => {
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return response.text(); 
  })
  .then(data => {
    setDomFromYaml(data);
  })
  .catch(error => {
    console.error('Error fetching file:', error);
  });
}

async function postJsonData(url, data) {
  //let url = '/cgi-bin/update_cfg.py';
  try {
    const response = await fetch(url, {
      method: 'POST', 
      headers: {
        'Content-Type': 'application/json' 
      },
      body: JSON.stringify(data) // Convert the JavaScript object to a JSON string
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const responseData = await response.json(); // Parse the JSON response
    //console.log('Success:', responseData);
    return responseData;
  } catch (error) {
    console.error('Error posting JSON data:', error);
    //throw error;
  }
}

function saveYamlFile(){
  let postData = {};

  for (let x=0; x < RADIO_VALUE_NAMES.length;x++){
    let domName = RADIO_VALUE_NAMES[x];
    postData[domName] = getRadioOptionValue(domName);
  }
  for (let x=0; x < CHECKBOX_VALUE_NAMES.length;x++){
    let domName = CHECKBOX_VALUE_NAMES[x];
    postData[domName] = document.getElementById(domName).checked;
  }
  for (let x=0; x < TEXT_VALUE_NAMES.length;x++){
    let domName = TEXT_VALUE_NAMES[x];

    try {
      postData[domName] = document.getElementById(domName).value;
    } catch (error) {
      console.log("Warning! Missing dom ID " + domName);
    }
  }
  for (let x=0; x < SELECT_VALUE_NAMES.length;x++){
    let domName = SELECT_VALUE_NAMES[x];
    try {
      postData[domName] = document.getElementById(domName).value;
    } catch (error) {
      console.log("Warning! Missing dom ID " + domName);
    }
  }

  postData['Skills'] = INSTALLED_SKILLS;

  let updateUrl = '/cgi-bin/update_cfg.py';
  postJsonData(updateUrl, postData)
    .then(result => {
      // Handle the successful response
      console.log("postJsonData result is ");
      console.log(result);
      alert("Configuration Saved");
    })
    .catch(error => {
      console.log(`postJsonData Error ${error}`);
    });
  }

function handleChkChanged(checkBoxObj, domId){
  let domObj = document.getElementById(domId);
  if (checkBoxObj.checked){
    domObj.style.display="inline-block";
  } else {
    domObj.style.display="none";
  }
}

function getOptionsFromKeys(selectedOption, optionNames){
  // given an object return the keys as options
  let res = '';
  for(optionName in optionNames){
    if (optionName == selectedOption){
      res += "<option selected>" + optionName + "</option>";
    } else {
      res += "<option>" + optionName + "</option>";
    }
  }
  return(res);
}

function getOptionsFromList(selectedOption, optionNames){
  let res = '';
  for(let x=0;x < optionNames.length;x++){
    if (selectedOption == optionNames[x]){
      res += "<option selected>" + optionNames[x] + "</option>";
    } else {
      res += "<option>" + optionNames[x] + "</option>";
    }
  }
  return(res);
}

function handleServiceChange(selectElement){
  // a service has changed
  let whichSvc = selectElement.options[selectElement.selectedIndex].value;
  let lmFlag = '';
  let modelOptions = [];
  if (selectElement.id == 'STTService'){
    let voiceSelect = "<select id=STTModel name=STTModel>";
    lmFlag = getRadioOptionValue("STT");
    if (lmFlag == 'local'){
      modelOptions = DRIVERS['stt_local'][whichSvc];
      document.getElementById('stt_model_select_div').innerHTML = voiceSelect + getOptionsFromList(LAST_LOCAL_STT_MODEL, modelOptions) + "</select>";
    } else {
      modelOptions = DRIVERS['stt_remote'][whichSvc];
      document.getElementById('stt_model_select_div').innerHTML = voiceSelect + getOptionsFromList(LAST_REMOTE_STT_MODEL, modelOptions) + "</select>";
    }
  } else {
    let voiceSelect = "<select id=TTSVoice name=TTSVoice>";
    lmFlag = getRadioOptionValue("TTS");
    if (lmFlag == 'local'){
      modelOptions = DRIVERS['tts_local'][whichSvc];
      document.getElementById('tts_voice_select_div').innerHTML = voiceSelect + getOptionsFromList(LAST_LOCAL_TTS_MODEL, modelOptions) + "</select>";
    } else {
      modelOptions = DRIVERS['tts_remote'][whichSvc];
      document.getElementById('tts_voice_select_div').innerHTML = voiceSelect + getOptionsFromList(LAST_REMOTE_TTS_MODEL, modelOptions) + "</select>";
    }
  }
}

function updateDrivers(){
  //console.log("UPDATE DRIVERS FROM THIS");
  //console.log(DRIVERS);

  // update TTS services
  let ttsWhich = getRadioOptionValue("TTS");
  let serviceOptions = '';
  let modelOptions = '';
  let voiceSelect = "<select id=TTSVoice name=TTSVoice>";
  let ttsSvc = LAST_REMOTE_TTS_SVC;
  if (ttsWhich == 'local'){
    ttsSvc = LAST_LOCAL_TTS_SVC;
    serviceOptions = getOptionsFromKeys(ttsSvc, DRIVERS['tts_local']);
    modelOptions = DRIVERS['tts_local'][ttsSvc];
    if (ttsSvc != ''){
      document.getElementById('tts_voice_select_div').innerHTML = voiceSelect + getOptionsFromList(LAST_LOCAL_TTS_MODEL, modelOptions) + "</select>";
    } else {
      document.getElementById('tts_voice_select_div').innerHTML = voiceSelect + "</select>";
    }
    document.getElementById('tts_remote').style.display = 'none';
    document.getElementById('tts_local').style.display = 'inline-block';
  } else {
    serviceOptions = getOptionsFromKeys(ttsSvc, DRIVERS['tts_remote']);
    modelOptions = DRIVERS['tts_remote'][ttsSvc];
    if (ttsSvc != ''){
      document.getElementById('tts_voice_select_div').innerHTML = voiceSelect + getOptionsFromList(LAST_REMOTE_TTS_MODEL, modelOptions) + "</select>";
    } else {
      document.getElementById('tts_voice_select_div').innerHTML = voiceSelect + "</select>";
    }
    document.getElementById('tts_local').style.display = 'none';
    document.getElementById('tts_remote').style.display = 'inline-block';
  }
  let selectHTML = `<select id=TTSService name=TTSService onchange="handleServiceChange(this);">`;
  selectHTML += serviceOptions;
  selectHTML += "</select>";
  document.getElementById('tts_where_select').innerHTML = selectHTML;

  // update STT services
  let sttWhich = getRadioOptionValue("STT");
  serviceOptions = '';
  modelOptions = '';
  voiceSelect = "<select id=STTModel name=STTModel>";
  let sttSvc = LAST_REMOTE_STT_SVC;
  if (sttWhich == 'local'){
    sttSvc = LAST_LOCAL_STT_SVC;
    serviceOptions = getOptionsFromKeys(sttSvc, DRIVERS['stt_local']);
    modelOptions = DRIVERS['stt_local'][sttSvc];
    if (sttSvc != ''){
      document.getElementById('stt_model_select_div').innerHTML = voiceSelect + getOptionsFromList(LAST_LOCAL_STT_MODEL, modelOptions) + "</select>";
    } else {
      document.getElementById('stt_model_select_div').innerHTML = voiceSelect + "</select>";
    }
    document.getElementById('stt_remote').style.display = 'none';
    document.getElementById('stt_local').style.display = 'inline-block';
  } else {
    serviceOptions = getOptionsFromKeys(sttSvc, DRIVERS['stt_remote']);
    modelOptions = DRIVERS['stt_remote'][sttSvc];
    if (sttSvc != ''){
      document.getElementById('stt_model_select_div').innerHTML = voiceSelect + getOptionsFromList(LAST_REMOTE_STT_MODEL, modelOptions) + "</select>";
    } else {
      document.getElementById('stt_model_select_div').innerHTML = voiceSelect + "</select>";
    }
    document.getElementById('stt_remote').style.display = 'inline-block';
    document.getElementById('stt_local').style.display = 'none';
  }
  selectHTML = `<select id=STTService name=STTService onchange="handleServiceChange(this);">`;
  selectHTML += serviceOptions;
  selectHTML += "</select>";
  document.getElementById('stt_where_select').innerHTML = selectHTML;
}

// start here
loadSkillsFile();

let driversUrl = '/cgi-bin/get_drivers.py';
let driversData = {'res':'None'};
postJsonData(driversUrl, driversData)
    .then(result => {
      // Handle the successful response
      DRIVERS = result['data'];

      // initial load we use cfg file values and establish defaults
	    
      // tts
      let ttsSvc = getCfgVal('TTSService');
      let ttsVoice = getCfgVal('TTSVoice');
      let ttsWhich = getCfgVal('TTS');
      if (ttsWhich == 'local'){
        LAST_LOCAL_TTS_SVC = ttsSvc;
        LAST_LOCAL_TTS_MODEL = ttsVoice;
        LAST_REMOTE_TTS_SVC = Object.keys(DRIVERS['tts_remote'])[0];
        LAST_REMOTE_TTS_MODEL = DRIVERS['tts_remote'][LAST_REMOTE_TTS_SVC][0];
      } else {
        LAST_REMOTE_TTS_SVC = ttsSvc;
        LAST_REMOTE_TTS_MODEL = ttsVoice;
        LAST_LOCAL_TTS_SVC = Object.keys(DRIVERS['tts_local'])[0];
        LAST_LOCAL_TTS_MODEL = DRIVERS['tts_local'][LAST_LOCAL_TTS_SVC][0];
      }

      // stt
      let sttSvc = getCfgVal('STTService');
      let sttModel = getCfgVal('STTModel');
      let sttWhich = getCfgVal('STT');
      if (sttWhich == 'local'){
        LAST_LOCAL_STT_SVC = sttSvc;
        LAST_LOCAL_STT_MODEL = sttModel;
        LAST_REMOTE_STT_SVC = Object.keys(DRIVERS['stt_remote'])[0];
        LAST_REMOTE_STT_MODEL = DRIVERS['stt_remote'][LAST_REMOTE_STT_SVC][0];
      } else {
        LAST_REMOTE_STT_SVC = sttSvc;
        LAST_REMOTE_STT_MODEL = sttModel;
        LAST_LOCAL_STT_SVC = Object.keys(DRIVERS['stt_local'])[0];
        LAST_LOCAL_STT_MODEL = DRIVERS['stt_local'][LAST_LOCAL_STT_SVC][0];
      }

      updateDrivers();
    })
    .catch(error => {
      console.log(`postJsonData Error ${error}`);
    });

