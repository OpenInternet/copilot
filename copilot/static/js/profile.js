
//Rule Defaults
// Ignore the ugly one liners.
var targetOptions = document.getElementById("all_targets").content.split("|").filter(function(el) {return el.length != 0});
var actionOptions = document.getElementById("all_actions").content.split("|").filter(function(el) {return el.length != 0});
var subTargetDefault = "internews.org";
var helpText = {}
helpText.action = "The action to be taken against the \"targeted\" traffic. e.g. block, throttle, redirect, or monitor."
helpText.target = "The type of network traffic to be targeted by this rule. e.g. HTTP, HTTPS, DNS, or URL."
helpText.subTarget = "A URL or ip-address that should be specifically targeted. (Use <strong>*</strong> to target ALL traffic."


//Add a rule to the rule list
function addRule() {
    // get id number for this item
    var idNum = getIdNum();

    //create group id
    var groupID = "rules-".concat(idNum, "-", "group");

    //Create the surrounding section
    var section = document.createElement("section");
    section.className = "section--center mdl-grid rule-section";
    section.id = groupID;

    //Create the spacer
    var spacerDiv = document.createElement("div");
    spacerDiv.className = "mdl-cell mdl-cell--2-col mdl-cell--hide-tablet= mdl-cell---hide-phone";
    section.appendChild(spacerDiv);

    //Create the rule card
    var ruleCard = document.createElement("div");
    ruleCard.className = "mdl-card rule-card mdl-cell mdl-cell--8-col mdl-shadow--4dp";
    // Added to section below
    //section.appendChild(ruleCard);

    //Create the rule card title
    var ruleTitleBox = document.createElement("div");
    ruleTitleBox.className = "mdl-card__title";


    //Create the rule card title
    var ruleTitle = document.createElement("h2");
    ruleTitle.className = "mdl-card__title-text";
    var ruleTitleText = document.createTextNode("Rule");
    ruleTitle.appendChild(ruleTitleText);
    ruleTitleBox.appendChild(ruleTitle);
    ruleCard.appendChild(ruleTitleBox);


    // Create rule card actions section
    var ruleCardActions = document.createElement("div");
    ruleCardActions.className = "mdl-card__actions mdl-card--border";
    // Added to rule card later
    //ruleCard.appendChild(ruleCardActions);


    // Create the surrounding row div
    var row = document.createElement("div");
    row.className = "row rule";

    // Create action rule sub components
    var actionSelector = addRuleSelector(idNum, "action", actionOptions);
    row.appendChild(actionSelector);

    // Create target rule sub components
    var targetSelector = addRuleSelector(idNum, "target", targetOptions);
    row.appendChild(targetSelector);

    // Create sub-target rule sub components
    var subTargetSelector = addRuleSelector(idNum, "sub_target", targetOptions);
    row.appendChild(subTargetSelector);

    //add row to rule card actions
    ruleCardActions.appendChild(row)
    ruleCard.appendChild(ruleCardActions);
    section.appendChild(ruleCard);


    // Get the list object
    var list = document.getElementById("rule_list");
    var addButton = document.getElementById("addButton");
    componentHandler.upgradeElement(section);
    list.insertBefore(section, addButton);
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
    ruleDiv.className = "mdl-textfield mdl-js-textfield mdl-textfield--floating-label getmdl-select mdl-cell mdl-cell--3-col ";

    //var label = document.createElement("label");
    //label.className = "mdl-textfield__label"
    //label.for = ruleID
    //get help text from above
    //var labelText = document.createTextNode(type);
    //label.appendChild(labelText);
    //ruleDiv.appendChild(label);

    // Create Data
    var data = createRuleData(type, ruleID, options);

    // Add table items to span
    ruleDiv.appendChild(data);

    //create help
    var tooltip = document.createElement("div");
    tooltip.className = "mdl-tooltip mdl-tooltip--large"
    tooltip.for = ruleID
    //get help text from above
    var tooltipText = document.createTextNode(helpText[type]);
    tooltip.appendChild(tooltipText);
    ruleDiv.appendChild(tooltip);

    return ruleDiv
}

//Creates a html rule object using material design select
// https://github.com/CreativeIT/getmdl-select
function createRuleData(type, ruleID, options) {
    var data;
    if (type == "action" || type == "target") {
        // Create input element
        data = document.createElement("select");
        data.className = "mdl-selectfield"

        // Don't display targets until actions have been chosen
        if (type == "target") {
            data.style.visibility = "hidden";
        }

        // Add all options to the select object
        var defaultOption = document.createElement("option");
        defaultOption.disabled = true;
        defaultOption.selected = true;
        defaultOption.value = "";
        var defaultContent = document.createTextNode("Choose your "+type);
        defaultOption.appendChild(defaultContent);
        data.appendChild(defaultOption);

        // Add all proper options to object
        for(var i = 0; i < options.length; i++) {
            // <option selected value="block">block</option>
            var dataOption = document.createElement("option");
            var dataContent = document.createTextNode(options[i]);
            dataOption.appendChild(dataContent);
            data.appendChild(dataOption);
        }
    } else if (type == "sub_target") {
        data = document.createElement("input");
        data.className = "mdl-textfield mdl-js-textfield";
        data.type = "text";
        data.value = subTargetDefault;
        data.style.visibility = "hidden";
    }

    //Set Generic Properties
    data.id = ruleID;
    data.addEventListener('click', function(){update_from_selector(ruleID)});
    data.name = ruleID;
    return data
}

//Gets the id number of the last rule in the rules group.
function getIdNum() {
    // get list of links with 'rules' class
    var curNum
    var links = document.getElementsByClassName('rule-section');
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

function update_from_selector(id) {
    console.log(id);
    var selector_type = id.split("-")[2]
    if (selector_type == "action") {
        update_from_action(id)
    } else if (selector_type == "target") {
        update_from_target(id)
    } else if (selector_type == "sub_target") {
        update_from_sub_target(id)
    }
}


//update the target based upon an action
function update_from_action(id) {
    var selector = document.getElementById(id)
    var idNum = id.split("-")[1]
    var selector_type = selector.options[selector.selectedIndex].value
    // get metadata object data of action target pairs
    var raw_targets = document.getElementById('pairs-'.concat(selector_type)).content;
    var targets = raw_targets.split("|").filter(function(el) {return el.length != 0})

    // get the target selector we will be modifying
    var targetObj = document.getElementById('rules-'.concat(idNum, "-", "target"));
    // clear all options from it
    targetObj.options.length=0
    targetObj.style.visibility = "visible"
    // repopulate the options
    for (i=0; i < targets.length; i++){
        targetObj.options[targetObj.options.length]=new Option(targets[i],  targets[i])
    }
}

function update_from_target(id) {
    var selector = document.getElementById(id)
    var idNum = id.split("-")[1]
    var selector_type = selector.options[selector.selectedIndex].value
    // get metadata object data of action target pairs
    var sub_target_list = document.getElementById('has_subtarget').content;
    var has_sub_targets = sub_target_list.split("|").filter(function(el) {return el.length != 0})
    console.log(sub_target_list)
    console.log(has_sub_targets)
    // get the target selector we will be modifying
    var subTargetObj = document.getElementById('rules-'.concat(idNum, "-", "sub_target"));
    if (has_sub_targets.indexOf(selector_type) > -1) {
        subTargetObj.style.visibility = "visible"
    } else {
        subTargetObj.style.visibility = "hidden"
    }
}

function update_from_sub_target(selector) {}
