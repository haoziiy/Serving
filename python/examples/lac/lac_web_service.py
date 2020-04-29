# Copyright (c) 2020 PaddlePaddle Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from paddle_serving_server.web_service import WebService
import sys
from lac_reader import LACReader


class LACService(WebService):
    def load_reader(self):
        self.reader = LACReader("lac_dict")

    def preprocess(self, feed={}, fetch=[]):
        batch_feed = []
        for ins in feed:
            if "words" not in ins:
                raise ("feed data error!")
            feed_data = self.reader.process(ins["words"])
            batch_feed.append({"words": feed_data})
        fetch = ["crf_decode"]
        return batch_feed, fetch

    def postprocess(self, feed={}, fetch=[], fetch_map={}):
        ret = []
        for idx, ins in enumerate(feed):
            segs = self.reader.parse_result(ins["words"],
                                            fetch_map[idx]["crf_decode"])
            ret.append({"word_seg": "|".join(segs)})
        return ret


lac_service = LACService(name="lac")
lac_service.load_model_config(sys.argv[1])
lac_service.load_reader()
lac_service.prepare_server(
    workdir=sys.argv[2], port=int(sys.argv[3]), device="cpu")
lac_service.run_server()
