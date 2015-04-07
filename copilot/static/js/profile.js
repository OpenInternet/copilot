
//Rule Defaults
var actionOptions = ["block"];
var targetOptions = ["dns", "url"];
var subTargetDefault = "foxnews.com";
var helpText = {}
helpText.action = ""
helpText.target = ""
helpText.subTarget = ""


//Add a rule to the rule list
function addRule() {
    // get id number for this item
    var idNum = getIdNum();

    //create group id
    var groupID = "rules-".concat(idNum, "-", "group");

    // Create the surrounding row div
    var row = document.createElement("div");
    row.className = "row rules";
    row.id = groupID;


    //Create deletion button
    //<div class="one columns">
    //<img src="{{ url_for('static', filename='images/delete_rule.png') }}" onclick="del_rule()">
    //</div>
    //create surounding column item
    var imgDiv = document.createElement("div");
    imgDiv.className = "one columns";
    //create image
    var delImage = document.createElement("img");
    delImage.src = "/static/images/delete_rule.png";
    delImage.onclick="delRule('".concat(groupID, "')");
    //append image to row
    imgDiv.appendChild(delImage);
    row.appendChild(imgDiv);

    // Create action rule sub components
    var actionSelector = addRuleSelector(idNum, "action", actionOptions);
    row.appendChild(actionSelector);

    // Create target rule sub components
    var targetSelector = addRuleSelector(idNum, "target", targetOptions);
    row.appendChild(targetSelector);

    // Create sub-target rule sub components
    var subTargetSelector = addRuleSelector(idNum, "sub_target", targetOptions);
    row.appendChild(subTargetSelector);

    // Get the list object
    var list = document.getElementById("rule_list");
    list.appendChild(row);
}

//This deletes the rule that uses this image.
function delRule(objID) {
    var ruleObj = document.getElementById(objID);
    ruleObj.parentElement.removeChild(ruleObj);
}


//Create a single rule selector html object containing action, target, and sub-target
function addRuleSelector(idNum, type, options) {
    var ruleID = "rules-".concat(idNum, "-", type);

    //Create span
    var ruleDiv = document.createElement("div");
    ruleDiv.className = "three columns";

    // Create Data
    var data = createRuleData(type, ruleID, actionOptions);

    // Add table items to span
    ruleDiv.appendChild(data);

    //create help
    //<div class="help"> {{help goes here}} </div>
    var help = document.createElement("div");
    help.className = "help"
    //get help text from above
    var text = document.createTextNode(helpText[type]);
    help.appendChild(text);
    ruleDiv.appendChild(help);

    return ruleDiv
}

//Creates a html rule object
// <select id="rules-0-action" class="u-full-width action" name="rules-0-action">
// <option value="block" selected="">block</option>
// </select>
function createRuleData(type, ruleID, options) {
    var data;
    if (type == "action" || type == "target") {
        // <select id="rules-2-action" name="rules-2-action">
        data = document.createElement("select");
        // Add all options to the select object
        for(var i = 0; i < options.length; i++) {
            // <option selected value="block">block</option>
            var dataOption = document.createElement("option");
            dataOption.value = options[i];
            var dataContent = document.createTextNode(options[i]);
            dataOption.appendChild(dataContent);
            data.appendChild(dataOption);
        }
        //Set the class of the data objects to be the name of the type of object that they are.
        data.className = type
    } else if (type == "sub_target") {
        data = document.createElement("input");
        data.type = "text"
        data.value = subTargetDefault
    }
    //Set Generic Properties
    data.id = ruleID
    data.className = "u-full-width {{ type }}"
    data.name = ruleID
    return data
}

//Gets the id number of the last rule in the rules group.
function getIdNum() {
    // get list of links with 'rules' class
    var curNum
    var links = document.getElementsByClassName('rule');
    if (typeof links !== 'undefined') {
        var last = links[links.length - 2]
        var lastID = last.id
        // Get the  id number for this item
        var idNum = lastID.split("-")[1]
        console.log(idNum)
        // add one to that number
        curNum = parseInt(idNum) + 1
    } else {
        curNum = 0
    }
    // return that number
    return curNum
}
