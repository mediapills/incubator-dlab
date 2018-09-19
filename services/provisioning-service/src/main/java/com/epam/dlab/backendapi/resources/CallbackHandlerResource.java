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

package com.epam.dlab.backendapi.resources;

import com.epam.dlab.backendapi.service.RestoreCallbackHandlerService;
import com.google.inject.Inject;
import lombok.extern.slf4j.Slf4j;

import javax.ws.rs.POST;
import javax.ws.rs.Path;
import javax.ws.rs.core.Response;

@Path("/handler")
@Slf4j
public class CallbackHandlerResource {
	private final RestoreCallbackHandlerService restoreCallbackHandlerService;

	@Inject
	public CallbackHandlerResource(RestoreCallbackHandlerService restoreCallbackHandlerService) {
		this.restoreCallbackHandlerService = restoreCallbackHandlerService;
	}

	@POST
	@Path("/restore")
	public Response restoreHandlers() {
		restoreCallbackHandlerService.restore();
		return Response.ok().build();
	}
}
