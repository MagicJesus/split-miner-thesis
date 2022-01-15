import sys


class CrawlerMerger:
    def __init__(self, crawlers):
        self.crawlers = crawlers

    @staticmethod
    def merge_crawlers(crawlers):
        final_crawler = None
        forced = True
        # print("MERGING CRAWLERS: ", len(crawlers))
        while len(crawlers) > 1:
            merged = False
            # find XOR relationships and merge them
            while 1:
                to_merge = []
                for crawler in crawlers:
                    for compare_crawler in crawlers:
                        if crawler != compare_crawler and crawler.is_xor(compare_crawler):
                            to_merge.append(compare_crawler)
                    if len(to_merge) > 0:
                        to_merge.append(crawler)
                        break
                if len(to_merge) > 0:
                    merged = True
                    final_crawler = DiagramCrawler.merge_xors(to_merge)
                    crawlers = [x for x in crawlers if x not in to_merge]
                    crawlers.append(final_crawler)
                else:
                    break

            ands_to_merge = []
            for crawler in crawlers:
                for compare_crawler in crawlers:
                    if crawler != compare_crawler and crawler.is_and(compare_crawler):
                        ands_to_merge.append(compare_crawler)
                if len(ands_to_merge) > 0:
                    ands_to_merge.append(crawler)
                    break
            if len(ands_to_merge) > 0:
                merged = True
                final_crawler = DiagramCrawler.merge_ands(ands_to_merge)
                crawlers = [x for x in crawlers if x not in ands_to_merge]
                crawlers.append(final_crawler)
            if not merged:
                min_distance = sys.maxsize
                for crawler in crawlers:
                    for compare_crawler in crawlers:
                        if crawler == compare_crawler:
                            continue
                        tmp_dist = crawler.get_anddistance(compare_crawler)
                        if tmp_dist < min_distance:
                            min_distance = tmp_dist
                            to_merge = [crawler, compare_crawler]
                if forced:
                    final_crawler = DiagramCrawler.forced_merge_ands(to_merge)
                    break
                else:
                    final_crawler = DiagramCrawler.merge_ands(to_merge)
        return final_crawler

    @staticmethod
    def merge_join_crawlers(crawlers):
        final_crawler = None
        forced = True
        # print("MERGING CRAWLERS: ", len(crawlers))
        while len(crawlers) > 1:
            merged = False
            # find XOR relationships and merge them
            while 1:
                to_merge = []
                for crawler in crawlers:
                    for compare_crawler in crawlers:
                        if crawler != compare_crawler and crawler.is_xor_join(compare_crawler):
                            to_merge.append(compare_crawler)
                    if len(to_merge) > 0:
                        to_merge.append(crawler)
                        break
                if len(to_merge) > 0:
                    merged = True
                    final_crawler = DiagramCrawler.merge_xor_joins(to_merge)
                    crawlers = [x for x in crawlers if x not in to_merge]
                    crawlers.append(final_crawler)
                else:
                    break

            ands_to_merge = []
            for crawler in crawlers:
                for compare_crawler in crawlers:
                    if crawler != compare_crawler and crawler.is_and_join(compare_crawler):
                        ands_to_merge.append(compare_crawler)
                if len(ands_to_merge) > 0:
                    ands_to_merge.append(crawler)
                    break
            if len(ands_to_merge) > 0:
                merged = True
                final_crawler = DiagramCrawler.merge_and_joins(ands_to_merge)
                crawlers = [x for x in crawlers if x not in ands_to_merge]
                crawlers.append(final_crawler)
            if not merged:
                min_distance = sys.maxsize
                for crawler in crawlers:
                    for compare_crawler in crawlers:
                        if crawler == compare_crawler:
                            continue
                        tmp_dist = crawler.get_anddistance(compare_crawler)
                        if tmp_dist < min_distance:
                            min_distance = tmp_dist
                            to_merge = [crawler, compare_crawler]
                if forced:
                    final_crawler = DiagramCrawler.forced_merge_and_joins(to_merge)
                    break
                else:
                    final_crawler = DiagramCrawler.merge_and_joins(to_merge)
        return final_crawler


class DiagramCrawler:
    def __init__(self):
        self.past = []
        self.future = []
        self.current = []
        self.past_string = ':'
        self.future_string = ':'
        self.current_string = ':'
        self.xor_siblings = []
        self.and_siblings = []

    def __str__(self):
        return f"*[Past: {self.past_string} Future: {self.future_string} Current: {self.current_string}]*"

    def __repr__(self):
        return f"*[Past: {self.past_string} Future: {self.future_string} Current: {self.current_string}]*"

    def __eq__(self, other):
        return str(self) == str(other)

    def __hash__(self):
        return hash(self.__key())

    def __key(self):
        return self.current_string

    def stringify(self):
        self.past.sort()
        self.future.sort()
        self.current = self.past + self.future
        self.current.sort()

        for item in self.past:
            self.past_string += str(item) + ":"

        for item in self.future:
            self.future_string += str(item) + ":"

        for item in self.current:
            self.current_string += str(item) + ":"

    def is_xor(self, other):
        return self.future_string == other.future_string

    def is_xor_join(self, other):
        return self.past_string == other.past_string

    @staticmethod
    def merge_xors(siblings):
        merged = DiagramCrawler()

        merged.xor_siblings = siblings
        merged.future = siblings[0].future
        for sibling in merged.xor_siblings:
            merged.past += sibling.past

        merged.stringify()

        return merged

    @staticmethod
    def merge_xor_joins(siblings):
        merged = DiagramCrawler()

        merged.xor_siblings = siblings
        merged.past = siblings[0].past
        for sibling in merged.xor_siblings:
            merged.future += sibling.future

        merged.stringify()

        return merged

    def is_and(self, other):
        return self.current_string == other.current_string

    def is_and_join(self, other):
        return self.current_string == other.current_string

    @staticmethod
    def merge_ands(siblings):
        merged = DiagramCrawler()

        merged.and_siblings = siblings

        for sibling in siblings:
            merged.future += sibling.future
        for sibling in siblings:
            merged.future = [x for x in merged.future if x in sibling.future]
        for sibling in siblings:
            merged.past += sibling.past

        merged.stringify()

        return merged

    @staticmethod
    def merge_and_joins(siblings):
        merged = DiagramCrawler()

        merged.and_siblings = siblings

        for sibling in siblings:
            merged.past += sibling.past
        for sibling in siblings:
            merged.past = [x for x in merged.past if x in sibling.past]
        for sibling in siblings:
            merged.future += sibling.future

        merged.stringify()

        return merged

    @staticmethod
    def forced_merge_ands(siblings):
        merged = DiagramCrawler()

        merged.and_siblings = siblings

        for sibling in siblings:
            merged.future += sibling.future
        for sibling in siblings:
            merged.past += sibling.past
        merged.future = [x for x in merged.future if x not in merged.past]

        merged.stringify()

        return merged

    def get_anddistance(self, other):
        union = []
        intersection = []

        for it in other.past:
            if it not in union:
                union.append(it)
        for it in other.future:
            if it not in union:
                union.append(it)

        for it in self.past:
            if it not in intersection:
                intersection.append(it)
        for it in self.future:
            if it not in intersection:
                intersection.append(it)

        intersection = [x for x in intersection if x in union]

        for it in self.past:
            if it not in union:
                union.append(it)
        for it in self.future:
            if it not in union:
                union.append(it)

        return len(union) - len(intersection)

    def add_past(self, to_add):
        self.past.append(to_add)

    def add_future(self, to_add):
        self.future.append(to_add)

    def get_node(self):
        if len(self.past) == 1:
            return self.past[0]
        else:
            return None

    def get_join_node(self):
        if len(self.future) == 1:
            return self.future[0]
        else:
            return None

    def get_gateway_type(self):
        if len(self.xor_siblings) > 0:
            return 'XOR'
        if len(self.and_siblings) > 0:
            return 'AND'
        return None

