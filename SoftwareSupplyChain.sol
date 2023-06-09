// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

import "./ERC20/SupplyChainToken.sol";

contract SoftwareSupplyChain {
    struct Developer {
        address id;
        string email;
        uint256 reliability;
        uint256 registration_date;
        uint256 last_update;
        uint256 report_num;
        uint256 interaction_points;
        uint256 reliability_bought;
        uint256 last_reliability_buy;
        string[] groups;
        mapping(string => uint256) groups_map;
        string[] groups_adm;
        mapping(string => uint256) groups_adm_map;
        string[] group_access_requests;
        mapping(string => uint256) group_access_requests_map;
        mapping(address => uint256) voted;
        mapping(address => uint256) reported;
    }

    struct DeveloperGroup {
        string name;
        address admin;
        address[] group_developers;
        mapping(address => uint256) group_developers_map;
        address[] to_be_approved;
        mapping(address => uint256) to_be_approved_map;
        string[] group_projects;
    }

    struct Project {
        string name;
        address admin;
        string[] library_versions;
        mapping(string => string) library_versions_map;
        string last_version;
        string group;
    }

    struct Library {
        string CID;
        string version;
        string project;
        uint256 reliability;
        address[] developed_by;
        string[] dependencies;
    }

    address public contract_owner;
    uint256 public devs_num;
    uint256 public groups_num;
    uint256 public projects_num;
    uint256 public libraries_num;
    uint256 public reliability_cost;

    uint256 private fees_paid;
    uint256 private total_developers_reliability;
    uint256 private total_libraries_reliability;
    uint256 private max_reliability;

    mapping(address => Developer) private developers;
    mapping(string => DeveloperGroup) private dev_groups;
    mapping(string => Project) private projects;
    mapping(string => Library) private libraries;
    mapping(string => address) private emails;

    event LibraryInfo(
        string version,
        string project,
        string[] dependencies,
        uint256 reliability,
        string level,
        uint256 mean
    );

    event Bought(uint256 amount);
    event Sold(uint256 amount);

    SupplyChainToken private sctContract;

    constructor(address sctAddress, uint256 max_rel, uint256 rel_cost) {
        sctContract = SupplyChainToken(sctAddress);
        contract_owner = msg.sender;
        max_reliability = max_rel;
        reliability_cost = rel_cost;
    }

    function addDeveloper(string memory _email) public {
        require(
            developers[msg.sender].id != msg.sender,
            "You are already registered as a developer"
        );
        require(
            emails[_email] == address(0),
            "A developer with the same email aready exists"
        );
        require(bytes(_email).length != 0, "Insert a valid email");
        require(
            sctContract.balanceOf(msg.sender) >= 3000,
            "You need 3000 SCT to register as a developer"
        );
        Developer storage dev = developers[msg.sender];
        dev.id = msg.sender;
        dev.email = _email;
        emails[_email] = msg.sender;
        dev.registration_date = block.timestamp;
        dev.last_update = block.timestamp;
        devs_num++;
        sctContract.transferFrom(msg.sender, address(this), 3000);
        fees_paid += 3000;
    }

    function createGroup(string memory group_name) public {
        require(
            developers[msg.sender].id == msg.sender,
            "You must register as a developer before you create a group"
        );
        require(bytes(group_name).length != 0, "The name can't be empty");
        require(
            bytes(dev_groups[group_name].name).length == 0,
            "A group with the same name aready exists"
        );
        require(
            sctContract.balanceOf(msg.sender) >= 2000,
            "You need 2000 SCT to create a group"
        );
        DeveloperGroup storage dev_group = dev_groups[group_name];
        developers[msg.sender].groups.push(group_name);
        developers[msg.sender].groups_map[group_name] = block.timestamp;
        developers[msg.sender].groups_adm.push(group_name);
        developers[msg.sender].groups_adm_map[group_name] = block.timestamp;
        dev_group.name = group_name;
        dev_group.admin = msg.sender;
        dev_group.group_developers.push(msg.sender);
        dev_group.group_developers_map[msg.sender] = dev_group
            .group_developers
            .length;
        groups_num++;
        sctContract.transferFrom(msg.sender, address(this), 2000);
        fees_paid += 2000;
    }

    function createProject(
        string memory group_name,
        string memory project_name
    ) public {
        require(
            bytes(dev_groups[group_name].name).length != 0,
            "Insert a valid group name"
        );
        require(
            bytes(project_name).length != 0,
            "The project name can't be empty"
        );
        require(
            dev_groups[group_name].admin == msg.sender,
            "You must be the admin of the group to create a project"
        );
        require(
            bytes(projects[project_name].name).length == 0,
            "A project with the same name already exists"
        );
        require(
            sctContract.balanceOf(msg.sender) >= 2000,
            "You need 2000 SCT to create a project"
        );
        Project storage project = projects[project_name];
        dev_groups[group_name].group_projects.push(project_name);
        project.name = project_name;
        project.group = group_name;
        project.admin = msg.sender;
        projects_num++;
        sctContract.transferFrom(msg.sender, address(this), 2000);
        fees_paid += 2000;
    }

    function requestGroupAccess(string memory group_name) public {
        require(
            developers[msg.sender].id == msg.sender,
            "You must register as a developer before you join a group"
        );
        require(
            developers[msg.sender].groups_map[group_name] == 0,
            "You are already a member of the group"
        );
        require(
            developers[msg.sender].group_access_requests_map[group_name] == 0,
            "You have already sent a request to this group"
        );
        require(
            bytes(dev_groups[group_name].name).length != 0,
            "Insert a valid group name"
        );
        dev_groups[group_name].to_be_approved.push(msg.sender);
        dev_groups[group_name].to_be_approved_map[msg.sender] = dev_groups[
            group_name
        ].to_be_approved.length;
        developers[msg.sender].group_access_requests.push(group_name);
        developers[msg.sender].group_access_requests_map[
            group_name
        ] = developers[msg.sender].group_access_requests.length;
    }

    function acceptGroupRequest(string memory group_name, address addr) public {
        require(
            bytes(dev_groups[group_name].name).length != 0,
            "Insert a valid group name"
        );
        require(
            dev_groups[group_name].admin == msg.sender,
            "You must be the admin of the group to accept requests"
        );
        require(
            dev_groups[group_name].to_be_approved_map[addr] != 0,
            "This developer has not requested to join the the group"
        );
        developers[addr].groups.push(group_name);
        developers[addr].groups_map[group_name] = developers[addr]
            .groups
            .length;
        uint256 adminCoeff;
        for (
            uint256 i = 0;
            i < dev_groups[group_name].group_developers.length;
            i++
        ) {
            if (
                dev_groups[group_name].admin ==
                developers[dev_groups[group_name].group_developers[i]].id
            ) {
                adminCoeff = 2;
            } else {
                adminCoeff = 1;
            }
            if (
                developers[addr].reliability >=
                (total_developers_reliability / devs_num) * 2
            ) {
                addReliabilityAndTokens(
                    developers[dev_groups[group_name].group_developers[i]].id,
                    2 * adminCoeff
                );
            } else if (
                developers[addr].reliability >=
                total_developers_reliability / devs_num
            ) {
                addReliabilityAndTokens(
                    developers[dev_groups[group_name].group_developers[i]].id,
                    1 * adminCoeff
                );
            }
        }
        if (
            developers[msg.sender].reliability >=
            (total_developers_reliability / devs_num) * 2
        ) {
            addReliabilityAndTokens(addr, 2);
        } else if (
            developers[msg.sender].reliability >=
            total_developers_reliability / devs_num
        ) {
            addReliabilityAndTokens(addr, 1);
        }
        dev_groups[group_name].group_developers.push(addr);
        dev_groups[group_name].group_developers_map[addr] = dev_groups[
            group_name
        ].group_developers.length;
        removeAddrFromArray(
            dev_groups[group_name].to_be_approved_map[addr] - 1,
            dev_groups[group_name].to_be_approved
        );
        removeStringFromArray(
            developers[addr].group_access_requests_map[group_name] - 1,
            developers[addr].group_access_requests
        );
        dev_groups[group_name].to_be_approved_map[addr] = 0;
        developers[addr].group_access_requests_map[group_name] = 0;
    }

    function removeDeveloperFromGroup(
        string memory group_name,
        address addr
    ) public {
        require(
            bytes(dev_groups[group_name].name).length != 0,
            "Insert a valid group name"
        );
        require(
            developers[addr].groups_map[group_name] != 0,
            "The developer is not part of the group"
        );
        require(
            dev_groups[group_name].admin == msg.sender,
            "You must be the admin of the group to remove a developer from it"
        );

        Developer storage dev = developers[addr];
        removeStringFromArray(
            developers[addr].groups_map[group_name] - 1,
            developers[addr].groups
        );
        removeAddrFromArray(
            dev_groups[group_name].group_developers_map[addr] - 1,
            dev_groups[group_name].group_developers
        );
        dev.groups_map[group_name] = 0;
        dev_groups[group_name].group_developers_map[addr] = 0;
    }

    function addLibrary(
        string memory project_name,
        string memory CID,
        string memory version,
        string[] memory dependencies
    ) public {
        require(
            projects[project_name].admin == msg.sender,
            "You must be the admin of the project to publish a library"
        );
        require(
            bytes(projects[project_name].name).length != 0,
            "Insert a valid project name"
        );
        require(bytes(CID).length != 0, "The CID can't be empty");

        if (bytes(dependencies[0]).length != 0) {
            for (uint256 i = 0; i < dependencies.length; i++) {
                require(
                    bytes(libraries[dependencies[i]].CID).length != 0,
                    "One of the dependencies CID is wrong"
                );
            }
        }
        require(
            !(bytes(projects[project_name].library_versions_map[version])
                .length !=
                0 ||
                bytes(libraries[CID].CID).length != 0),
            "The same version already exists"
        );
        require(
            sctContract.balanceOf(msg.sender) >= 1000,
            "You need 1000 SCT to add a library version to a project"
        );
        Library storage lib = libraries[CID];
        lib.CID = CID;
        lib.version = version;
        lib.dependencies = dependencies;
        lib.project = project_name;

        address[] memory devs = dev_groups[projects[project_name].group]
            .group_developers;
        uint256 len = devs.length;
        for (uint256 i = 0; i < len; i++) {
            lib.developed_by.push(developers[devs[i]].id);
        }

        uint256 rel = computeReliability(CID);
        lib.reliability = rel;
        total_libraries_reliability += rel;
        libraries_num++;
        projects[project_name].library_versions.push(CID);
        projects[project_name].last_version = CID;
        projects[project_name].library_versions_map[version] = CID;
        sctContract.transferFrom(msg.sender, address(this), 1000);
        fees_paid += 1000;
    }

    function voteDeveloper(address developer) public {
        require(
            developers[msg.sender].id == msg.sender,
            "You must register as a developer before you vote another developer"
        );
        require(msg.sender != developer, "You can't vote for yourself");
        require(
            developers[developer].id == developer,
            "Insert a valid developer address"
        );
        require(
            developers[msg.sender].voted[developer] == 0,
            "The developers was already voted"
        );
        addReliabilityAndTokens(developer, 10);
        developers[msg.sender].voted[developer] = block.timestamp;
    }

    function reportDeveloper(address developer) public {
        require(
            developers[msg.sender].id == msg.sender,
            "You must register as a developer before you report another developer"
        );
        require(msg.sender != developer, "You can't report yourself");
        require(
            developers[developer].id == developer,
            "Insert a valid developer address"
        );
        require(
            developers[msg.sender].reported[developer] == 0,
            "The developers was already reported"
        );
        developers[developer].reliability -= 10;
        total_developers_reliability -= 10;
        developers[developer].report_num++;
        developers[msg.sender].reported[developer] = block.timestamp;
    }

    function updateReliability() public {
        require(
            block.timestamp - developers[msg.sender].last_update >= 432000,
            "Too little time has passed since the last update"
        );
        uint256 time = block.timestamp - developers[msg.sender].last_update;
        uint256 rel = time / 432000;
        addReliabilityAndTokens(msg.sender, rel);
        developers[msg.sender].last_update += rel * 432000;
    }

    function changeAdmin(address new_admin, string memory group_name) public {
        require(
            dev_groups[group_name].admin == msg.sender,
            "You must be the admin of the group to appoint another admin in your place"
        );
        require(
            developers[new_admin].id == new_admin,
            "The new admin must be a registered developer"
        );
        dev_groups[group_name].admin = new_admin;
        for (
            uint256 i = 0;
            i < dev_groups[group_name].group_projects.length;
            i++
        ) {
            projects[dev_groups[group_name].group_projects[i]]
                .admin = new_admin;
        }
    }

    function buyTokens() public payable {
        uint256 tokens = msg.value * 1;
        require(tokens > 0, "You need to send some ether");
        require(
            tokens <= sctContract.balanceOf(address(this)),
            "Not enough tokens in the reserve"
        );
        sctContract.transfer(msg.sender, tokens);
        emit Bought(tokens);
    }

    function sellTokens(uint256 amount) public {
        require(amount > 0, "You need to sell at least some tokens");
        uint256 allowance = sctContract.allowance(msg.sender, address(this));
        require(allowance >= amount, "Check the token allowance");
        sctContract.transferFrom(msg.sender, address(this), amount);
        payable(msg.sender).transfer(amount);
        emit Sold(amount);
    }

    function buyReliability(uint256 reliability) public {
        require(
            developers[msg.sender].id == msg.sender,
            "You must register as a developer before you buy reliability"
        );
        require(
            balanceOf(msg.sender) >= reliability * reliability_cost,
            "You don't have enough SCT"
        );
        Developer storage dev = developers[msg.sender];
        if (block.timestamp - dev.last_reliability_buy >= 2592000) {
            dev.reliability_bought = 0;
        }
        require(
            dev.reliability_bought + reliability < max_reliability,
            "You bought the maximum number of reliability, wait 30 days"
        );
        if (dev.reliability_bought == 0) {
            dev.last_reliability_buy = block.timestamp;
        }
        sctContract.transferFrom(
            msg.sender,
            address(this),
            reliability * reliability_cost
        );
        dev.reliability_bought += reliability;
        dev.reliability += reliability;
        total_developers_reliability += reliability;
        fees_paid += reliability * reliability_cost;
    }

    function balanceOf(address token_owner) public view returns (uint256) {
        return sctContract.balanceOf(token_owner);
    }

    function getDeveloperInformation(
        address addr
    ) public view returns (string memory, uint256, uint256) {
        return (
            developers[addr].email,
            developers[addr].reliability,
            developers[addr].registration_date
        );
    }

    function getGroups(address addr) public view returns (string[] memory) {
        return developers[addr].groups;
    }

    function getAdminGroups(
        address addr
    ) public view returns (string[] memory) {
        return developers[addr].groups_adm;
    }

    function getGroupProjects(
        string memory group_name
    ) public view returns (string[] memory) {
        return dev_groups[group_name].group_projects;
    }

    function getGroupAccessRequests(
        address addr
    ) public view returns (string[] memory) {
        return developers[addr].group_access_requests;
    }

    function getToBeApproved(
        string memory group_name
    ) public view returns (address[] memory) {
        return dev_groups[group_name].to_be_approved;
    }

    function getProjectVersions(
        string memory project_name
    ) public view returns (string[] memory) {
        return projects[project_name].library_versions;
    }

    function getProjectLastVersion(
        string memory project_name
    ) public view returns (string memory) {
        return projects[project_name].last_version;
    }

    function getLibraryInformation(
        string memory CID
    )
        public
        view
        returns (
            string memory,
            string memory,
            string[] memory,
            uint256 reliability
        )
    {
        return (
            libraries[CID].version,
            libraries[CID].project,
            libraries[CID].dependencies,
            computeReliability(CID)
        );
    }

    function getLibraryInformationWithLevel(string memory CID) public {
        uint256 rel = computeReliability(CID);
        uint256 rel_diff = rel - libraries[CID].reliability;
        libraries[CID].reliability = rel;
        total_libraries_reliability += rel_diff;
        for (
            uint256 i = 0;
            i <
            dev_groups[projects[libraries[CID].project].group]
                .group_developers
                .length;
            i++
        ) {
            Developer storage curr_dev = developers[
                dev_groups[projects[libraries[CID].project].group]
                    .group_developers[i]
            ];
            curr_dev.interaction_points++;
            if (curr_dev.interaction_points % 1000 == 0) {
                addReliabilityAndTokens(curr_dev.id, 1);
            }
        }
        string memory level;
        uint256 reliability_mean = total_libraries_reliability / libraries_num;
        if (rel <= (reliability_mean * 1) / 3) {
            level = "Very Low";
        } else if (rel <= (reliability_mean * 2) / 3) {
            level = "Low";
        } else if (rel <= (reliability_mean * 3) / 2) {
            level = "Medium";
        } else if (rel <= (reliability_mean * 2)) {
            level = "High";
        } else {
            level = "Very High";
        }
        emit LibraryInfo(
            libraries[CID].version,
            libraries[CID].project,
            libraries[CID].dependencies,
            rel,
            level,
            reliability_mean
        );
    }

    function getDeveloperAddressFromEmail(
        string memory email
    ) public view returns (address) {
        return emails[email];
    }

    function computeReliability(
        string memory CID
    ) private view returns (uint256) {
        address[] memory devs = libraries[CID].developed_by;
        uint256 len = devs.length;
        uint256 sum = 0;
        for (uint256 i = 0; i < len; i++) {
            if (developers[devs[i]].reliability < 0) {
                return 0;
            }
            if (
                developers[devs[i]].id == projects[libraries[CID].project].admin
            ) {
                sum += 2 * developers[devs[i]].reliability;
            } else {
                sum += developers[devs[i]].reliability;
            }
        }

        return sum / len;
    }

    function removeStringFromArray(
        uint256 index,
        string[] storage array
    ) private {
        if (index >= array.length) return;

        for (uint256 i = index; i < array.length - 1; i++) {
            array[i] = array[i + 1];
        }
        array.pop();
    }

    function removeAddrFromArray(
        uint256 index,
        address[] storage array
    ) private {
        if (index >= array.length) return;

        for (uint256 i = index; i < array.length - 1; i++) {
            array[i] = array[i + 1];
        }
        array.pop();
    }

    function addReliabilityAndTokens(address dev, uint256 reliability) private {
        developers[dev].reliability += reliability;
        total_developers_reliability += reliability;
        if (fees_paid >= reliability) {
            sctContract.transfer(dev, reliability);
            fees_paid -= reliability;
        }
    }
}
