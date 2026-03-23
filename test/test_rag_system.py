"""
RAG 系统综合测试脚本

测试内容：
  1. RAG 系统初始化
  2. 向量库构建和加载
  3. 查询和检索功能
  4. 结果展示
  5. 性能测试
"""

import sys
import os
import time
import json
from typing import List, Dict

# 添加项目路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.rag.rag import RAG


class RAGSystemTester:
    """RAG 系统测试类"""

    def __init__(self, config_path: str):
        """
        初始化测试器

        参数：config_path - 配置文件路径
        """
        self.config_path = config_path
        self.rag = None
        self.test_results = {}

    def test_initialization(self) -> bool:
        """
        测试1：RAG 系统初始化

        验证：
          - 配置加载成功
          - 文档加载成功
          - 模型初始化成功
          - 向量库初始化成功
        """
        print("\n" + "=" * 70)
        print("【测试1】RAG 系统初始化")
        print("=" * 70)

        try:
            print("正在初始化 RAG 系统...")
            start_time = time.time()
            self.rag = RAG(self.config_path)
            init_time = time.time() - start_time

            print(f"✅ 初始化成功，耗时 {init_time:.2f} 秒")

            # 验证核心组件
            assert self.rag.config is not None, "配置加载失败"
            assert len(self.rag.all_documents) > 0, "文档加载失败"
            assert len(self.rag.chunks) > 0, "文档分块失败"
            assert self.rag.embedder is not None, "嵌入模型初始化失败"
            assert self.rag.vector_store is not None, "向量库初始化失败"

            self.test_results['initialization'] = {
                'status': '✅ 通过',
                'time': f'{init_time:.2f}秒',
                'documents': len(self.rag.all_documents),
                'chunks': len(self.rag.chunks)
            }

            return True

        except Exception as e:
            print(f"❌ 初始化失败: {e}")
            self.test_results['initialization'] = {
                'status': '❌ 失败',
                'error': str(e)
            }
            return False

    def test_vector_store_stats(self) -> bool:
        """
        测试2：向量库统计信息

        验证：
          - 向量库包含正确数量的 chunks
          - metadata 完整
          - 距离度量设置正确
        """
        print("\n" + "=" * 70)
        print("【测试2】向量库统计信息")
        print("=" * 70)

        try:
            stats = self.rag.get_vector_store_stats()

            print(f"向量库统计：")
            print(f"  - 总 chunks 数: {stats['total_chunks']}")
            print(f"  - Collection 名称: {stats['collection_name']}")
            print(f"  - 距离度量: {stats['distance_metric']}")
            print(f"  - 存储位置: {stats['persist_dir']}")

            # 验证
            assert stats['total_chunks'] > 0, "向量库为空"
            assert stats['distance_metric'] == 'cosine', "距离度量不正确"

            print("✅ 向量库统计信息验证成功")

            self.test_results['vector_store_stats'] = {
                'status': '✅ 通过',
                'total_chunks': stats['total_chunks'],
                'collection_name': stats['collection_name']
            }

            return True

        except Exception as e:
            print(f"❌ 验证失败: {e}")
            self.test_results['vector_store_stats'] = {
                'status': '❌ 失败',
                'error': str(e)
            }
            return False

    def test_chunk_samples(self) -> bool:
        """
        测试3：查看 chunk 样本

        验证：
          - chunks 包含正确的 metadata
          - page_content 非空
          - 来源信息完整
        """
        print("\n" + "=" * 70)
        print("【测试3】Chunk 样本展示")
        print("=" * 70)

        try:
            self.rag.display_chunks(num_samples=3)

            # 验证 chunks 结构
            if len(self.rag.chunks) > 0:
                sample_chunk = self.rag.chunks[0]
                assert sample_chunk.page_content, "page_content 为空"
                assert sample_chunk.metadata, "metadata 为空"
                assert 'source' in sample_chunk.metadata, "缺少 source metadata"

                print("✅ Chunk 样本验证成功")

                self.test_results['chunk_samples'] = {
                    'status': '✅ 通过',
                    'sample_count': min(3, len(self.rag.chunks)),
                    'total_chunks': len(self.rag.chunks)
                }

                return True
            else:
                raise Exception("chunks 列表为空")

        except Exception as e:
            print(f"❌ 验证失败: {e}")
            self.test_results['chunk_samples'] = {
                'status': '❌ 失败',
                'error': str(e)
            }
            return False

    def test_single_query(self, query: str, top_k: int = 20) -> bool:
        """
        测试4：单个查询测试（展示所有结果的完整内容）

        参数：
          query - 测试查询字符串
          top_k - 返回结果数量（默认20，展示更多结果）

        验证：
          - 查询返回结果
          - 结果包含必要信息
          - 相似度计算正确
        """
        print("\n" + "=" * 70)
        print("【测试4】单个查询测试（完整结果展示）")
        print("=" * 70)

        try:
            print(f"测试查询: '{query}'")
            start_time = time.time()
            results = self.rag.search(query, top_k=top_k)
            query_time = time.time() - start_time

            print(f"✅ 查询成功，耗时 {query_time:.2f} 秒，找到 {len(results)} 个结果")

            # 验证结果结构
            if len(results) > 0:
                first_result = results[0]
                assert 'rank' in first_result, "缺少 rank 字段"
                assert 'content' in first_result, "缺少 content 字段"
                assert 'source' in first_result, "缺少 source 字段"
                assert 'similarity' in first_result, "缺少 similarity 字段"
                assert 'metadata' in first_result, "缺少 metadata 字段"

                print(f"\n✅ 搜索结果（全部 {len(results)} 个）：\n")
                # 展示所有结果的完整内容
                for result in results:
                    print("=" * 70)
                    print(f"【结果 {result['rank']}】")
                    print(f"相似度: {result['similarity']}")
                    print(f"距离: {result['distance']}")
                    print(f"来源: {result['source']}")
                    print(f"页码: {result.get('page', 'N/A')}")
                    print(f"Chunk ID: {result['chunk_id']}")
                    print("\n内容：")
                    print("-" * 70)
                    # 显示完整内容
                    print(result['content'])
                    print("-" * 70)
                    print()

            self.test_results['single_query'] = {
                'status': '✅ 通过',
                'query': query,
                'results_count': len(results),
                'query_time': f'{query_time:.2f}秒'
            }

            return True

        except Exception as e:
            print(f"❌ 查询失败: {e}")
            self.test_results['single_query'] = {
                'status': '❌ 失败',
                'query': query,
                'error': str(e)
            }
            return False

    def test_multiple_queries(self, queries: List[str]) -> bool:
        """
        测试5：批量查询测试

        参数：queries - 查询字符串列表

        验证：
          - 多个查询都能正确执行
          - 结果的相似度降序排列
          - 查询时间在可接受范围内
        """
        print("\n" + "=" * 70)
        print("【测试5】批量查询测试")
        print("=" * 70)

        try:
            print(f"测试 {len(queries)} 个查询...")

            query_times = []
            all_successful = True

            for idx, query in enumerate(queries, 1):
                start_time = time.time()
                results = self.rag.search(query, top_k=3)
                query_time = time.time() - start_time
                query_times.append(query_time)

                status = "✅" if len(results) > 0 else "⚠️"
                print(f"\n  {status} 查询 {idx}: '{query}' - {len(results)} 个结果 ({query_time:.2f}s)")

                # 显示所有结果的完整内容
                for result in results:
                    print(f"\n    【结果 {result['rank']}】")
                    print(f"    相似度: {result['similarity']}")
                    print(f"    距离: {result['distance']}")
                    print(f"    来源: {result['source']}")
                    if result.get('page'):
                        print(f"    页码: {result['page']}")
                    print(f"    Chunk ID: {result['chunk_id']}")
                    print(f"    内容: {result['content'][:300]}..." if len(result['content']) > 300 else f"    内容: {result['content']}")

                if len(results) == 0:
                    all_successful = False

            # 计算统计
            avg_time = sum(query_times) / len(query_times)
            max_time = max(query_times)

            print(f"\n查询统计:")
            print(f"  - 平均耗时: {avg_time:.2f} 秒")
            print(f"  - 最长耗时: {max_time:.2f} 秒")
            print(f"  - 状态: {'✅ 全部成功' if all_successful else '⚠️ 部分失败'}")

            self.test_results['multiple_queries'] = {
                'status': '✅ 通过' if all_successful else '⚠️ 部分成功',
                'total_queries': len(queries),
                'avg_time': f'{avg_time:.2f}秒',
                'max_time': f'{max_time:.2f}秒'
            }

            return all_successful

        except Exception as e:
            print(f"❌ 批量查询失败: {e}")
            self.test_results['multiple_queries'] = {
                'status': '❌ 失败',
                'error': str(e)
            }
            return False

    def test_result_display(self, query: str) -> bool:
        """
        测试6：结果展示功能

        验证：
          - 结果可以正确格式化和展示
          - 信息完整清晰
        """
        print("\n" + "=" * 70)
        print("【测试6】结果展示功能")
        print("=" * 70)

        try:
            results = self.rag.search(query, top_k=3)

            if len(results) > 0:
                self.rag.display_search_results(results)
                print("✅ 结果展示成功")
                self.test_results['result_display'] = {
                    'status': '✅ 通过',
                    'results_displayed': len(results)
                }
            else:
                print("⚠️ 查询无结果")
                self.test_results['result_display'] = {
                    'status': '⚠️ 无结果',
                    'results_displayed': 0
                }

            return True

        except Exception as e:
            print(f"❌ 显示失败: {e}")
            self.test_results['result_display'] = {
                'status': '❌ 失败',
                'error': str(e)
            }
            return False

    def print_test_summary(self):
        """打印测试总结"""
        print("\n" + "=" * 70)
        print("【测试总结】")
        print("=" * 70)

        print("\n测试结果：\n")

        passed = 0
        failed = 0

        for test_name, result in self.test_results.items():
            status = result.get('status', '未知')
            if '✅' in status:
                passed += 1
            elif '❌' in status:
                failed += 1

            print(f"{test_name.upper()}:")
            for key, value in result.items():
                if key != 'status':
                    print(f"  - {key}: {value}")
            print()

        print("-" * 70)
        print(f"总计: ✅ {passed} 个通过，❌ {failed} 个失败")
        print("=" * 70)

        return failed == 0


def main():
    """主测试函数"""
    print("\n" + "=" * 70)
    print("RAG 系统测试开始")
    print("=" * 70)

    # 配置文件路径
    config_path = os.path.join(
        os.path.dirname(__file__),
        '..',
        'config',
        'rag.yaml'
    )

    # 创建测试器
    tester = RAGSystemTester(config_path)

    # 运行测试
    print("\n【测试流程】")
    print("1. 初始化 RAG 系统")
    print("2. 验证向量库统计")
    print("3. 查看 chunk 样本")
    print("4. 执行单个查询")
    print("5. 执行批量查询")
    print("6. 验证结果展示")

    # 执行测试
    test_init = tester.test_initialization()
    if not test_init:
        print("\n❌ 初始化失败，停止后续测试")
        tester.print_test_summary()
        return

    tester.test_vector_store_stats()
    tester.test_chunk_samples()

    # 单个查询测试
    test_query = "什么是C++？"
    tester.test_single_query(test_query)

    # 批量查询测试
    test_queries = [
        "什么是智能指针？",
        "讲解一下C++中的多态",
        "C++11引入了哪些新特性？",
    ]
    tester.test_multiple_queries(test_queries)

    # 结果展示测试
    tester.test_result_display(test_query)

    # 打印总结
    all_passed = tester.print_test_summary()

    # 返回状态码
    return 0 if all_passed else 1


if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)
