/*
 *
 *  * Copyright (c) 2018, EPAM SYSTEMS INC
 *  *
 *  * Licensed under the Apache License, Version 2.0 (the "License");
 *  * you may not use this file except in compliance with the License.
 *  * You may obtain a copy of the License at
 *  *
 *  *     http://www.apache.org/licenses/LICENSE-2.0
 *  *
 *  * Unless required by applicable law or agreed to in writing, software
 *  * distributed under the License is distributed on an "AS IS" BASIS,
 *  * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 *  * See the License for the specific language governing permissions and
 *  * limitations under the License.
 *
 */
package com.epam.dlab.backendapi.dao;

import com.epam.dlab.backendapi.resources.dto.UserRoleDto;
import com.google.inject.Singleton;
import com.mongodb.client.result.UpdateResult;
import org.bson.Document;

import java.util.Date;
import java.util.List;
import java.util.Set;

import static com.mongodb.client.model.Filters.eq;
import static com.mongodb.client.model.Filters.in;

@Singleton
public class UserRoleDaoImpl extends BaseDAO implements UserRoleDao {

	private static final String USERS_FIELD = "users";
	private static final String GROUPS_FIELD = "groups";


	@Override
	public List<UserRoleDto> getUserRoles() {
		return find(MongoCollections.ROLES, UserRoleDto.class);
	}

	@Override
	public void insert(UserRoleDto dto) {
		insertOne(MongoCollections.ROLES, dto, dto.getId());
	}

	@Override
	public boolean update(UserRoleDto dto) {
		final Document userRoleDocument = convertToBson(dto).append(TIMESTAMP, new Date());
		return conditionMatched(updateOne(MongoCollections.ROLES,
				eq(ID, dto.getId()),
				new Document(SET, userRoleDocument)));
	}

	@Override
	public boolean addUserToRole(Set<String> users, Set<String> roleIds) {
		return conditionMatched(updateMany(MongoCollections.ROLES, in(ID, roleIds), addToSet(USERS_FIELD, users)));
	}

	@Override
	public boolean addGroupToRole(Set<String> groups, Set<String> roleIds) {
		return conditionMatched(updateMany(MongoCollections.ROLES, in(ID, roleIds), addToSet(GROUPS_FIELD,
				groups)));
	}

	@Override
	public boolean removeUserFromRole(Set<String> users, Set<String> roleIds) {
		return conditionMatched(updateMany(MongoCollections.ROLES, in(ID, roleIds), pullAll(USERS_FIELD, users)));
	}

	@Override
	public boolean removeGroupFromRole(Set<String> groups, Set<String> roleIds) {
		return conditionMatched(updateMany(MongoCollections.ROLES, in(ID, roleIds), pullAll(GROUPS_FIELD, groups)));
	}

	@Override
	public void remove(String roleId) {
		deleteOne(MongoCollections.ROLES, eq(ID, roleId));
	}

	private boolean conditionMatched(UpdateResult updateResult) {
		return updateResult.getMatchedCount() > 0;
	}

}