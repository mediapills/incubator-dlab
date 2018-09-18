/*
 * **************************************************************************
 *
 * Copyright (c) 2018, EPAM SYSTEMS INC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
 * ***************************************************************************
 */

package com.epam.dlab.backendapi.dao;

import com.epam.dlab.backendapi.resources.dto.UserRoleDto;

import java.util.List;
import java.util.Set;

public interface UserRoleDao {
	List<UserRoleDto> getUserRoles();

	void insert(UserRoleDto dto);

	boolean update(UserRoleDto dto);

	boolean addUserToRole(Set<String> users, Set<String> roleIds);

	boolean addGroupToRole(Set<String> groups, Set<String> roleIds);

	boolean removeUserFromRole(Set<String> users, Set<String> roleIds);

	boolean removeGroupFromRole(Set<String> groups, Set<String> roleIds);

	void remove(String roleId);
}