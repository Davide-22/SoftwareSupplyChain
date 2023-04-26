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
        string[] dependencies;
    }

    address public contract_owner = msg.sender;
    uint256 public devs_num;
    uint256 public groups_num;
    uint256 public projects_num;
    uint256 public libraries_num;
    uint256 private total_developers_reliability;
    uint256 private total_libraries_reliability;
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

    SupplyChainToken private sctContract;

    constructor(address sctAddress) {
        sctContract = SupplyChainToken(sctAddress);
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
        /*require(
            sstContract.balanceOf(msg.sender) >= 20,
            "You need 20 SCT to register as a developer"
        );*/
        Developer storage dev = developers[msg.sender];
        dev.id = msg.sender;
        dev.email = _email;
        emails[_email] = msg.sender;
        dev.reliability = 0;
        dev.registration_date = block.timestamp;
        dev.last_update = block.timestamp;
        devs_num++;
        //sctContract.approve(sctContract.contract_owner(), 20);
        //sctContract.transferFrom(msg.sender, sctContract.contract_owner(), 20);
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
        DeveloperGroup storage dev_group = dev_groups[group_name];
        developers[msg.sender].groups.push(group_name);
        developers[msg.sender].groups_map[group_name] = block.timestamp;
        developers[msg.sender].groups_adm.push(group_name);
        developers[msg.sender].groups_adm_map[group_name] = block.timestamp;
        dev_group.name = group_name;
        dev_group.admin = msg.sender;
        dev_group.group_developers.push(msg.sender);
        groups_num++;
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
        Project storage project = projects[project_name];
        dev_groups[group_name].group_projects.push(project_name);
        project.name = project_name;
        project.group = group_name;
        project.admin = msg.sender;
        projects_num++;
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
            "You must be the admin of the group to accept request"
        );
        require(
            dev_groups[group_name].to_be_approved_map[addr] != 0,
            "This developer has not requested to join the the group"
        );
        developers[addr].groups.push(group_name);
        developers[addr].groups_map[group_name] = block.timestamp;
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
                developers[dev_groups[group_name].group_developers[i]]
                    .reliability += 2 * adminCoeff;
            } else if (
                developers[addr].reliability >=
                total_developers_reliability / devs_num
            ) {
                developers[dev_groups[group_name].group_developers[i]]
                    .reliability += 1 * adminCoeff;
            }
        }
        if (
            developers[msg.sender].reliability >=
            (total_developers_reliability / devs_num) * 2
        ) {
            developers[addr].reliability += 2;
        } else if (
            developers[msg.sender].reliability >=
            total_developers_reliability / devs_num
        ) {
            developers[addr].reliability += 1;
        }
        dev_groups[group_name].group_developers.push(addr);
        removeAddrFromArray(
            dev_groups[group_name].to_be_approved_map[addr] - 1,
            dev_groups[group_name].to_be_approved
        );
        removeStringFromArray(
            developers[addr].group_access_requests_map[group_name] - 1,
            developers[addr].group_access_requests
        );
        return;
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
        Library storage lib = libraries[CID];
        lib.CID = CID;
        lib.version = version;
        lib.dependencies = dependencies;
        lib.project = project_name;
        uint256 rel = computeReliability(CID);
        lib.reliability = rel;
        total_libraries_reliability += rel;
        libraries_num++;
        projects[project_name].library_versions.push(CID);
        projects[project_name].last_version = CID;
        projects[project_name].library_versions_map[version] = CID;
    }

    function voteDeveloper(address developer) public {
        require(
            developers[msg.sender].id == msg.sender,
            "You must register as a developer before you vote another developer"
        );
        require(msg.sender != developer, "You can't vote yourself");
        require(
            developers[developer].id == developer,
            "Insert a valid developer address"
        );
        require(
            developers[msg.sender].voted[developer] == 0,
            "The developers was already voted"
        );
        developers[developer].reliability += 10;
        total_developers_reliability += 10;
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
        developers[msg.sender].reliability += rel;
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
    }

    function buyTokens() public payable {
        uint256 tokens = msg.value * 1;
        require(sctContract.balanceOf(sctContract.contract_owner()) >= tokens);
        sctContract.transfer(msg.sender, tokens);
    }

    function balanceOf(address tokenOwner) public view returns (uint256) {
        return sctContract.balanceOf(tokenOwner);
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
        string memory level;
        uint256 reliability_mean = total_libraries_reliability / libraries_num;
        if (rel <= (reliability_mean * 1) / 3) {
            level = "Very low";
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
        address[] memory devs = dev_groups[
            projects[libraries[CID].project].group
        ].group_developers;
        uint256 len = devs.length;
        uint256 sum = 0;
        for (uint256 i = 0; i < len; i++) {
            sum += developers[devs[i]].reliability;
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
}
