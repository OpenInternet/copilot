
//Rule Defaults
// Ignore the ugly one liners.
var targetOptions = document.getElementById("all_targets").content.split(" ").filter(function(el) {return el.length != 0});
var actionOptions = document.getElementById("all_actions").content.split(" ").filter(function(el) {return el.length != 0});
var subTargetDefault = "internews.org";
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
    row.className = "row rule";
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
    delImage.onclick = function() { delRule(groupID); };
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
    var addButton = document.getElementById("addButton");
    componentHandler.upgradeElement(row);
    list.insertBefore(row, addButton);
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
    var data = createRuleData(type, ruleID, options);

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
    data.id = ruleID;
    data.addEventListener('click', update_from_action)
/*    var onclickstring = "update_from_";
    data.onclick = onclickstring.concat(type, "(this)");*/
    data.className = "u-full-width " + type;
    data.name = ruleID;
    return data
}

//Gets the id number of the last rule in the rules group.
function getIdNum() {
    // get list of links with 'rules' class
    var curNum
    var links = document.getElementsByClassName('rule');
    var last = links[links.length - 1]
    if (typeof last !== 'undefined') {
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


//update the target based upon an action
function update_from_action(selector) {
    var idNum = selector.id.split("-")[1]
    // get metadata object data of action target pairs
    var raw_targets = document.getElementById('pairs-'.concat(selector.value)).content;
    var targets = raw_targets.split(" ").filter(function(el) {return el.length != 0})

    // get the target selector we will be modifying
    var targetObj = document.getElementById('rules-'.concat(idNum, "-", "target"));
    // clear all options from it
    targetObj.options.length=0
    // repopulate the options
    for (i=0; i < targets.length; i++){
        targetObj.options[targetObj.options.length]=new Option(targets[i],  targets[i])
    }
}

function update_from_target(selector) {}
function update_from_sub_target(selector) {}
